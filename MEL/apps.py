from django.apps import AppConfig

from MEL.services.download_service import download_base_datasets
SECTION_DETAILS_DATASET_LINK = "https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2024.zip"
CANDIDATE_DETAILS_DATASET_LINK = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2024.zip"
dataset_links = [SECTION_DETAILS_DATASET_LINK, CANDIDATE_DETAILS_DATASET_LINK]

# Path to save the downloaded zip file
section_zip_file_path = "SECTION_DETAILS_DATASET.zip"
candidate_zip_file_path = "CANDIDATE_DETAILS_DATASET.zip"
zip_files_path = [section_zip_file_path, candidate_zip_file_path]
DATA_PATH = "."

all_candidates_file_sub_str = "candidato"
all_sections_file_sub_str = "secao"

class MelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "MEL"


    def ready(self) -> None:
        download_base_datasets(dataset_links, zip_files_path, DATA_PATH)