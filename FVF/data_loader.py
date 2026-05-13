import pandas as pd
import streamlit as st 
import requests
from io import BytesIO
import os

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
PORJECT_ID = "1681"
BRANCH = "main"
BASE_URL = f"https://gitlab.internal.ftth.iliad.fr/api/v4/projects/1681/repository/files"


def _get_latest_file(prefix: str) -> str:
    url = f"https://gitlab.internal.ftth.iliad.fr/api/v4/projects/1681/repository/tree?ref={BRANCH}&per_page=100"
    r = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    r.raise_for_status()
    files = [f["name"] for f in r.json() if f["name"].startswith(prefix) and f["name"].endswith(".xlsx")]
    if not files:
        raise FileNotFoundError(f"Aucun fichier trouvé avec le préfixe {prefix}")
    return sorted(files)[-1]  # le plus récent alphabétiquement (date dans le nom)
def _fetch_excel(filename:str)->pd.DataFrame:
    url = f"{BASE_URL}/{filename}/raw?ref={BRANCH}"
    r = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    r.raise_for_status()
    return pd.read_excel(BytesIO(r.content))

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    df_cnd = _fetch_excel(_get_latest_file("telematique__cnd"))
    df_cnc = _fetch_excel(_get_latest_file("telematique__cnc"))
    
    df_cnd.columns = df_cnd.columns.str.strip().str.lower()
    df_cnc.columns = df_cnc.columns.str.strip().str.lower()

    df_cnd["by_date"] = pd.to_datetime(df_cnd["by_date"])
    df_cnc["by_date"] = pd.to_datetime(df_cnc["by_date"])
    print("CND columns:", df_cnd.columns.tolist())
    print("CNC columns:", df_cnc.columns.tolist())
    df_cnd["id_irm"] = pd.to_numeric(df_cnd["id_irm"], errors="coerce")
    df_cnc["id_irm"] = pd.to_numeric(df_cnc["id_irm"], errors="coerce")

    ids_a_exclure = df_cnd[df_cnd["distance_parcourue_en_km"] > 1000]["id_irm"].unique()
    df_cnd = df_cnd[~df_cnd["id_irm"].isin(ids_a_exclure)]
    return df_cnc, df_cnd  