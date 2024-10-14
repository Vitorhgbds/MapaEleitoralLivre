#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from MEL.services.download_service import download_base_datasets
SECTION_DETAILS_DATASET_LINK = "https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2024.zip"
CANDIDATE_DETAILS_DATASET_LINK = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2024.zip"
dataset_links = [SECTION_DETAILS_DATASET_LINK, CANDIDATE_DETAILS_DATASET_LINK]

# Path to save the downloaded zip file
section_zip_file_path = "SECTION_DETAILS_DATASET.zip"
candidate_zip_file_path = "CANDIDATE_DETAILS_DATASET.zip"
zip_files_path = [section_zip_file_path, candidate_zip_file_path]
DATA_PATH = "DATA"

all_candidates_file_sub_str = "candidato"
all_sections_file_sub_str = "secao"



def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MapaEleitoralLivre.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Check if running in a PyInstaller bundle and disable the auto-reloader
    if getattr(sys, 'frozen', False):
        sys.argv.append('--noreload')
        
    download_base_datasets(dataset_links, zip_files_path, DATA_PATH)
    
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
