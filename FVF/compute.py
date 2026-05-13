import pandas as pd

def _enrich(df_agg: pd.DataFrame, df_cnd: pd.DataFrame) -> pd.DataFrame:
    info = df_cnd[["id_irm", "nom_irm", "prenom_irm", "immatriculation"]].drop_duplicates("id_irm")
    return df_agg.merge(info, on="id_irm", how="left")

def top10_global(df_cnd: pd.DataFrame, service_choisi: str = "Tous") -> pd.DataFrame:
    df = df_cnd[df_cnd["is_hp"] == 1].copy()
    if service_choisi != "Tous":
        df = df[df["service_irm"] == service_choisi]
    agg = (
        df.groupby("id_irm")["distance_parcourue_en_km"]
        .sum()
        .reset_index()
        .rename(columns={"distance_parcourue_en_km": "total_km_hp"})
        .sort_values("total_km_hp", ascending=False)
        .head(10)
    )
    result = _enrich(agg, df_cnd)
    result = result[result["nom_irm"].notna() & (result["nom_irm"] != "")]
    result = result[result["prenom_irm"].notna() & (result["prenom_irm"] != "")]
    result["rang"] = range(1, len(result) + 1)
    return result[["rang", "nom_irm", "prenom_irm", "id_irm", "immatriculation", "total_km_hp"]]

def top10_par_mois(df_cnd: pd.DataFrame, mois_choisi: str, service_choisi: str = "Tous") -> pd.DataFrame:
    df = df_cnd[df_cnd["is_hp"] == 1].copy()
    df["mois"] = df["by_date"].dt.to_period("M")
    if service_choisi != "Tous":
        df = df[df["service_irm"] == service_choisi]
    df_mois = df[df["mois"] == mois_choisi]
    agg = (
        df_mois.groupby("id_irm")["distance_parcourue_en_km"]
        .sum()
        .reset_index()
        .rename(columns={"distance_parcourue_en_km": "total_km_hp"})
        .sort_values("total_km_hp", ascending=False)
        .head(10)
    )
    result = _enrich(agg, df_cnd)
    result = result[result["nom_irm"].notna() & (result["nom_irm"] != "")]
    result = result[result["prenom_irm"].notna() & (result["prenom_irm"] != "")]
    result["rang"] = range(1, len(result) + 1)
    return result[["rang", "nom_irm", "prenom_irm", "id_irm", "immatriculation", "total_km_hp"]]