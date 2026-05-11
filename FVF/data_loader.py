import pandas as pd
import streamlit as st 
import requests
from io import BytesIO
import os

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
PORJECT_ID = "1681"
BRANCH = "main"
BASE_URL = f"https://gitlab.internal.ftth.iliad.fr/api/v4/projects/1681/repository/files"
FILE_CND = os.getenv("FILE_CND", "telematique__cnd-2026-05-11.xlsx")
FILE_CNC = os.getenv("FILE_CNC", "telematique__cnc-2026-05-11.xlsx")

def _fetch_excel(filename:str)->pd.DataFrame:
    url = f"{BASE_URL}/{filename}/raw?ref={BRANCH}"
    r = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    r.raise_for_status()
    return pd.read_excel(BytesIO(r.content))

@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    df_cnd = _fetch_excel(FILE_CND)
    df_cnc = _fetch_excel(FILE_CNC)
    
    df_cnd.columns = df_cnd.columns.str.strip().str.lower()
    df_cnc.columns = df_cnc.columns.str.strip().str.lower()

    df_cnd["by_date"] = pd.to_datetime(df_cnd["by_date"])
    df_cnc["by_date"] = pd.to_datetime(df_cnc["by_date"])
    print("CND columns:", df_cnd.columns.tolist())
    print("CNC columns:", df_cnc.columns.tolist())
    df_cnd["id_irm"] = pd.to_numeric(df_cnd["id_irm"], errors="coerce")
    df_cnc["id_irm"] = pd.to_numeric(df_cnc["id_irm"], errors="coerce")
    return df_cnc, df_cnd  