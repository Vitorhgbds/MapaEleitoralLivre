import requests
import zipfile
import os
import pandas as pd


def download_base_datasets(dataset_links: list[str], zip_file_names: list[str], data_path: str) -> None:
    
    for i,dataset_link in enumerate(dataset_links):
        
        zip_file_path = f"{data_path}/{zip_file_names[i]}"
        response = requests.get(dataset_link)
        
        with open(zip_file_path, 'wb') as f:
            f.write(response.content)

        # Unzip the file and extract only the file that ends with 'BRASIL.csv'
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # List of files in the zip
            zip_file_list = zip_ref.namelist()
            
            # Find the file that ends with 'BRASIL.csv'
            for file in zip_file_list:
                if file.endswith("BRASIL.csv"):
                    # Extract only the BRASIL.csv file
                    zip_ref.extract(file, path=data_path)
                    print(f"Extracted: {file}")

        # Clean up by removing the zip file after extraction
        os.remove(zip_file_path)
        
        
def find_file_by_substring(dir: str, substring: str) -> str:
    # Get all file names in the folder
    file_names = os.listdir(dir)
    file_path = ""
    # Print all file names
    for file_name in file_names:
        if substring in file_name:
            file_path = f"{dir}/{file_name}"
            return file_path
    # Step 3: Read the CSV file with the correct encoding (e.g., ISO-8859-1 or windows-1252)
    return file_path
    