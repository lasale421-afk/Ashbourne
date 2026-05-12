import pandas as pd
import requests
from io import BytesIO
import os
from datetime import date

# Charger les données
from data_loader import load_data
from compute import top10_global, top10_par_mois

def export_excel():
    df_cnd, df_cnc = load_data()
    
    today = date.today().strftime("%Y-%m-%d")
    filename = f"top10_fraude_{today}.xlsx"
    
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        # Onglet global
        df_global = top10_global(df_cnd, df_cnc)
        df_global.to_excel(writer, sheet_name="Top10 Global", index=False)
        
        # Onglet par mois
        df_cnd_copy = df_cnd.copy()
        df_cnd_copy["mois"] = pd.to_datetime(df_cnd_copy["by_date"]).dt.to_period("M")
        mois_disponibles = sorted(df_cnd_copy["mois"].unique(), reverse=True)
        
        for mois in mois_disponibles[-3:]:
            df_mois = top10_par_mois(df_cnd, df_cnc, str(mois))
            df_mois.to_excel(writer, sheet_name=str(mois), index=False)
    
    print(f"Export généré : {filename}")
    return filename

if __name__ == "__main__":
    export_excel()