import pandas as pd
import os
from datetime import date
from data_loader import load_data_raw

def generate_alertes():
    df_cnd = load_data_raw()
    print(df_cnd["distance_parcourue_en_km"].max())
    today = date.today().strftime("%Y-%m-%d")
    ids_alertes = df_cnd[df_cnd["distance_parcourue_en_km"] > 1000][
        ["id_irm", "nom_irm", "prenom_irm", "immatriculation", "service_irm","distance_parcourue_en_km"]
    ].drop_duplicates("id_irm").sort_values("id_irm")

    if ids_alertes.empty:
        print("Aucune alerte détectée.")
        print(df_cnd["distance_parcourue_en_km"].sort_values(ascending=False).head(10))
        return

    filename = os.path.abspath(f"alertes_fichier_original_{today}.xlsx")
    ids_alertes.to_excel(filename, index=False, engine="openpyxl")
    print(f"{len(ids_alertes)} personnes avec trajets > 1000km détectées.")
    print(f"Fichier généré : {filename}")
    
if __name__ == "__main__":
    generate_alertes()