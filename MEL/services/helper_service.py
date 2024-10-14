import pandas as pd

def prepare_filters(file_path) -> dict[str,list[str]]:
    df = pd.read_csv(file_path, encoding='ISO-8859-1',sep=';',dtype=str)
    
    return {
        "SG_UF":sorted(df["SG_UF"].unique()),
        "NM_MUNICIPIO":sorted(df["NM_MUNICIPIO"].unique()),
        "NR_ZONA":sorted(df["NR_ZONA"].unique()),
        "NR_SECAO":sorted(df["NR_SECAO"].unique()),
    }
    
    
def filter_base_dataframe(filters: dict[str,list[str]], base_df_path: str) -> list[dict[str,str]]:
    sections_df = pd.read_csv(base_df_path, encoding='ISO-8859-1',sep=';',dtype=str)
    base_df = sections_df[["CD_ELEICAO","NR_ZONA","NR_SECAO","SG_UF","NM_MUNICIPIO","CD_MUNICIPIO","NM_LOCAL_VOTACAO","DS_LOCAL_VOTACAO_ENDERECO"]].drop_duplicates()
    
    # Apply filters from the dictionary
    for col, values in filters.items():
        # Apply case-insensitive check for "todos" and filter accordingly
        if not any("todos".upper() == v.upper() for v in values):
            base_df = base_df[base_df[col].isin(values)]
    
    # Return the filtered DataFrame
    base_df.reset_index(drop=True, inplace=True)
    return base_df