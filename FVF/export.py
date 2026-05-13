import pandas as pd
import os
import win32com.client
from datetime import date
from data_loader import load_data
from compute import top10_global

def get_top3_services(df_cnd, df_cnc):
    df_merged = df_cnd.merge(df_cnc[["id_irm", "service"]], on="id_irm", how="left")
    return (
        df_merged[df_merged["service"].notna() & (df_merged["service"] != "(null)")]
        .groupby("service")["distance_parcourue_en_km"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .index.tolist()
    )

def export_service(df_cnd, df_cnc, service, today):
    """Génère un fichier Excel pour un service donné."""
    # Filtrer par service
    ids_service = df_cnc[df_cnc["service"] == service]["id_irm"].unique()
    df_cnd_service = df_cnd[df_cnd["id_irm"].isin(ids_service)]
    df_cnc_service = df_cnc[df_cnc["service"] == service]

    # Top 10 du service
    df_top10 = top10_global(df_cnc_service, df_cnd_service)

    # Nom du fichier - enlever les caractères spéciaux pour Windows
    service_clean = "".join(c for c in service if c.isalnum() or c in " _-").strip()
    filename = os.path.abspath(f"top10_fraude_{service_clean}_{today}.xlsx")

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        # Onglet Top 10
        df_top10.to_excel(writer, sheet_name="Top 10", index=False)

        # Un onglet par personne du top 10
        for _, row in df_top10.iterrows():
            id_irm = row["id_irm"]
            nom = f"{row['prenom_irm']} {row['nom_irm']}"[:31]

            df_detail = df_cnd[
                (df_cnd["id_irm"] == id_irm) &
                (df_cnd["is_hp"] == 1)
            ][["immatriculation", "id_irm", "nom_irm", "prenom_irm", "by_date", "distance_parcourue_en_km"]]

            df_detail.to_excel(writer, sheet_name=nom, index=False)

    print(f"Export généré : {filename}")
    return filename

def send_mail(filepaths):
    """Envoie les fichiers par mail via Outlook."""
    outlook = win32com.client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)
    mail.To = 'ngeniteau@iliad-free.fr'
    mail.Subject = f'[Télématique] Top 10 Fraude Kilométrique - {date.today().strftime("%d/%m/%Y")}'
    mail.Body = 'Bonjour,\n\nVeuillez trouver en pièce jointe les rapports hebdomadaires des 3 services avec le plus de km hors journée de travail.\n\nCordialement'

    for filepath in filepaths:
        mail.Attachments.Add(filepath)

    mail.Send()
    print(f"Mail envoyé à ngeniteau@iliad-free.fr")

def export_excel():
    df_cnc, df_cnd = load_data()
    today = date.today().strftime("%Y-%m-%d")

    top3_services = get_top3_services(df_cnd, df_cnc)
    print(f"Top 3 services : {top3_services}")

    filepaths = []
    for service in top3_services:
        filepath = export_service(df_cnd, df_cnc, service, today)
        filepaths.append(filepath)

    send_mail(filepaths)

if __name__ == "__main__":
    export_excel()