from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed
import os

global progress
global goal




def extract(base_information_dataframe, base_candidates_path, progress_callback, turno) -> list[dict[str,str]] | None:
    if base_information_dataframe.empty:
        return None
    
    full_name_pattern = r'^\d+\s+[\wÀ-ÖØ-öø-ÿ]+(\s+[\wÀ-ÖØ-öø-ÿ]+)*$'
    digit_only_pattern = r'^\d+.*$'

    BASE_URL = "https://resultados.tse.jus.br/oficial/app/index.html#/eleicao;"
    LAST_URL = "/dados-de-urna/boletim-de-urna"

    CD_ELEICAO = base_information_dataframe["CD_ELEICAO"].iloc[0]
    n_turno = int(CD_ELEICAO) + 1
        
    if turno == "todos":
        CD_ELEICAO = [CD_ELEICAO, n_turno]
    elif int(turno) > 1:
        CD_ELEICAO = [n_turno]
    else:
        CD_ELEICAO = [CD_ELEICAO]
        
    SG_UF_LIST = base_information_dataframe["SG_UF"].unique()
    
    base_candidates_df = pd.read_csv(base_candidates_path, encoding='ISO-8859-1',sep=';',dtype=str)
    base_candidates_df_filtered = base_candidates_df[["NM_URNA_CANDIDATO", "NR_CANDIDATO", "CD_MUNICIPIO","DS_CARGO","SG_PARTIDO"]].drop_duplicates()
    
    global goal
    global progress
    goal = int(base_information_dataframe.shape[0]) * len(CD_ELEICAO)
    progress = 0
    # Maximum threads based on CPU count
    max_threads = os.cpu_count()
    
    for cd_eleicao in CD_ELEICAO:
        for uf in SG_UF_LIST:
            # Filter the DataFrame where 'uf' equals 'SG_UF'
            filtered_uf_df = base_information_dataframe[base_information_dataframe['SG_UF'] == uf]
            CD_MU_LIST = filtered_uf_df["CD_MUNICIPIO"].unique()
            progress_callback(progress, goal, uf)
            candidates_result = []
            for cd_mu in CD_MU_LIST:
                filtered_mu_df = filtered_uf_df[filtered_uf_df['CD_MUNICIPIO'] == cd_mu]
                ZN_LIST = filtered_mu_df["NR_ZONA"].unique()

                # Using ThreadPoolExecutor for concurrent threads
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(fetch_zona_information, filtered_mu_df[filtered_mu_df['NR_ZONA'] == nr_zona]["NR_SECAO"].unique(),
                                        cd_eleicao, uf, cd_mu, nr_zona, progress_callback)
                        for nr_zona in ZN_LIST
                    ]
                    
                    # Collect results as they complete
                    for future in as_completed(futures):
                        candidates_result.extend(future.result())
                    
            flattened_data = [item for sublist in candidates_result for item in sublist]
            candidates_df = pd.DataFrame(flattened_data)
            # Get current date and time
            current_datetime = datetime.now()
            # Convert to string in the desired format
            datetime_str = current_datetime.strftime("%Y%m%d%H%M%S")
            candidates_merged_df = pd.merge(base_candidates_df_filtered,candidates_df, on=["CD_MUNICIPIO","NR_CANDIDATO"],how='inner')
            candidates_completed = pd.merge(candidates_merged_df, base_information_dataframe, on=['NR_SECAO', 'NR_ZONA','CD_MUNICIPIO'], how='inner')
            candidates_completed["CD_ELEICAO"] = cd_eleicao
            candidates_completed.to_csv(f'extraction_{datetime_str}_{uf}_e{cd_eleicao}.csv', index=False, sep=";")
        

    return candidates_completed.to_dict(orient="records")
                

def fetch_zona_information(ns_list, cd_eleicao,uf,cd_mu,nr_zona, progress_callback) -> list[dict[str,str]]:
    global goal
    global progress
    full_name_pattern = r'^\d+\s+[\wÀ-ÖØ-öø-ÿ]+(\s+[\wÀ-ÖØ-öø-ÿ]+)*$'
    digit_only_pattern = r'^\d+.*$'

    BASE_URL = "https://resultados.tse.jus.br/oficial/app/index.html#/eleicao;"
    LAST_URL = "/dados-de-urna/boletim-de-urna"
    driver = fetch_firefox_driver()
    candidates_result = []
    for nr_secao in ns_list:
        filters = f"e=e{cd_eleicao};uf={uf.lower()};mu={cd_mu};ufbu={uf.lower()};mubu={cd_mu};zn={nr_zona};se={nr_secao}"
        full_url = f"{BASE_URL}{filters}{LAST_URL}"
        print(full_url)
        
        candidates_roles_elements = fetch_candidates_elements(full_url, driver, digit_only_pattern)
        candidates = fetch_ballot_box_candidates_information(candidates_roles_elements, nr_secao, nr_zona,cd_mu)
        candidates_result.append(candidates)
        progress += 1
        progress_callback(progress, goal, uf)
    driver.quit() 
    return candidates_result


def fetch_firefox_driver(driver_options = None):
    if not driver_options:
        # Set up headless Firefox
        driver_options = Options()
        driver_options.add_argument("--headless")
        # Initialize WebDriver with headless options

        # Set Firefox preferences to allow geolocation automatically
        profile = webdriver.FirefoxProfile()
        profile.set_preference("geo.prompt.testing", True)
        profile.set_preference("geo.prompt.testing.allow", True)
        profile.set_preference('dom.webdriver.enabled', False)
        profile.set_preference('useAutomationExtension', False)
        profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0")

        driver_options.profile = profile
    
    driver = webdriver.Firefox(options=driver_options)
    return driver


def has_valid_candidate(driver, candidate_name_pattern):
    """
    Checks if the page contains any valid candidate elements.
    """
    p_elements = driver.find_elements(By.TAG_NAME, "p")
    
    for p_element in p_elements:
        candidate_name_cleaned = p_element.text.strip().upper()
        if re.match(candidate_name_pattern, candidate_name_cleaned, re.UNICODE):
            return True  # Valid candidate found
    return False  # No valid candidates found yet


def wait_for_valid_candidate(driver, candidate_name_pattern):
    """
    Waits until at least one valid candidate (based on name pattern) is found on the page.
    """
    # Try to find valid candidate in the list of elements
    WebDriverWait(driver, 5).until(lambda d: has_valid_candidate(d, candidate_name_pattern))


def load_ballot_box_page(url: str, driver, candidate_name_pattern, max_retries=7):
    driver.get(url)
    # Wait for the main element to load (initial load)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "captureDiv"))
    )

    # Retry logic for refreshing and waiting for valid candidates
    retries = 0
    while retries < max_retries:
        try:
            # Optionally refresh the page to make sure it's fully loaded
            time.sleep(1)
            driver.refresh()

            # Wait for the element with candidates to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cargo-fixo"))
            )

            # Wait until valid candidates are present
            wait_for_valid_candidate(driver, candidate_name_pattern)
            
            # If we reach this point, valid candidates were found, return the driver
            return driver
        
        except Exception as e:
            # Increment retry counter
            retries += 1
            print(f"Retry {retries} failed. Reason: {str(e)}")
        
    # If we exhaust retries, raise an exception or handle it as needed
    raise Exception(f"Failed to load valid candidates after {max_retries} retries.")
    

def fetch_ballot_box_roles_candidates_html(driver):
    rendered_html = driver.page_source
    soup = BeautifulSoup(rendered_html, 'html.parser')
    ballot_box_information_html = soup.find(id='captureDiv')
    roles_candidates = ballot_box_information_html.find_all(class_='cargo-fixo')
    return roles_candidates


def fetch_candidates_elements(full_url:str, driver, candidate_name_pattern):
    candidates_elements_by_role = {}
    try:
        driver = load_ballot_box_page(full_url,driver,candidate_name_pattern)
        roles_candidates = fetch_ballot_box_roles_candidates_html(driver)

        for role in roles_candidates:
            
            # parent can be a table with VEREADOR or PREFEITO
            parent = role.find_parent()
            
            # P elements represents the name of each candidate
            p_elements = parent.find_all('p')
            
            # H1 represents candidate role title
            position_title = role.find('h1')
            
            for p_element in p_elements:
                name = clean_candidate_name_from_element(p_element).strip()
                if re.match(candidate_name_pattern, name, re.UNICODE):
                    role_name = position_title.text.strip().upper()
                    candidates_elements_by_role[role_name] = candidates_elements_by_role.get(role_name,[]) + [p_element]
        
        return candidates_elements_by_role
    except Exception as e:
        print(e)


def clean_candidate_name_from_element(p_element):
    candidate_name_cleaned = p_element.text.strip().upper()
    return candidate_name_cleaned


def collect_candidate_number_from_element(p_element):
    candidate_name_cleaned = clean_candidate_name_from_element(p_element)
    candidate_name_splitted = candidate_name_cleaned.split(" ")
    NR_CANDIDATO = candidate_name_splitted[0]
    return NR_CANDIDATO


def collect_candidate_name_from_element(p_element):
    candidate_name_cleaned = clean_candidate_name_from_element(p_element)
    candidate_name_splitted = candidate_name_cleaned.split(" ")
    NM_CANDIDATO = None
    if len(candidate_name_splitted) > 1:
        NM_CANDIDATO = " ".join(candidate_name_splitted[1:])
    return NM_CANDIDATO


def collect_candidate_votes_from_element(p_element) -> str:
    """Collects 

    Args:
        p_element (_type_): _description_

    Returns:
        dict[str,str] | None: _description_
    """
    
    p_parent = p_element.find_parent()
    votes_title_element = p_parent.find(class_='titulo-sm')
    total_votes_element = votes_title_element.find_next_sibling()
    TOTAL_VOTOS = total_votes_element.text.strip()
    
    return TOTAL_VOTOS

    
def fetch_ballot_box_candidates_information(candidates_role_elements: dict,  nr_secao: str, nr_zona: str, cd_mu: str) -> list[dict[str,str]]:
    
    candidates = []
    
    for role, p_elements in candidates_role_elements.items():
        for p_element in p_elements:
            candidate_nr = collect_candidate_number_from_element(p_element)
            candidate_votes = collect_candidate_votes_from_element(p_element)
            candidates.append(
                {
                    "NR_CANDIDATO": candidate_nr,
                    "TOTAL_VOTOS": candidate_votes,
                    "NR_ZONA": nr_zona,
                    "NR_SECAO": nr_secao,
                    "CD_MUNICIPIO": cd_mu,
                }
            )
        
    return candidates

