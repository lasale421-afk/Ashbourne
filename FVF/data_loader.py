import pandas as pd
import streamlit as st
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
BRANCH = "main"
BASE_URL = f"https://gitlab.internal.ftth.iliad.fr/api/v4/projects/1681/repository/files"


def _get_latest_file(prefix: str) -> str:
    url = f"https://gitlab.internal.ftth.iliad.fr/api/v4/projects/1681/repository/tree?ref={BRANCH}&per_page=100"
    r = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    r.raise_for_status()
    files = [f["name"] for f in r.json() if f["name"].startswith(prefix) and (f["name"].endswith(".xlsx") or f["name"].endswith(".csv"))]
    if not files:
        raise FileNotFoundError(f"Aucun fichier trouvé avec le préfixe {prefix}")
    return sorted(files)[-1]


def _fetch_excel(filename: str) -> pd.DataFrame:
    url = f"{BASE_URL}/{filename}/raw?ref={BRANCH}"
    r = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    r.raise_for_status()
    if filename.endswith(".csv"):
        return pd.read_csv(BytesIO(r.content), sep=";")
    return pd.read_excel(BytesIO(r.content))

@st.cache_data
def load_data() -> pd.DataFrame:
    df_cnd = _fetch_excel(_get_latest_file("telematique__cnd"))

    df_cnd.columns = df_cnd.columns.str.strip().str.lower()
    df_cnd["by_date"] = pd.to_datetime(df_cnd["by_date"])
    df_cnd["distance_parcourue_en_km"] = pd.to_numeric(df_cnd["distance_parcourue_en_km"], errors="coerce")

    # Filtre trajets 
    ids_a_exclure = df_cnd[df_cnd["distance_parcourue_en_km"] > 1000]["id_irm"].unique()
    df_cnd = df_cnd[~df_cnd["id_irm"].isin(ids_a_exclure)]

    print("CND columns:", df_cnd.columns.tolist())
    return df_cnd