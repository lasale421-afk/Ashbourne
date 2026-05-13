import pandas as pd 

def _enrich(df_agg: pd.DataFrame, df_cnc: pd.DataFrame) -> pd.DataFrame:
    info = df_cnc[["id_irm", "nom_irm", "prenom_irm", "immatriculation"]].drop_duplicates("id_irm")
    return df_agg.merge(info, on="id_irm", how="left")

def top10_global(df_cnd: pd.DataFrame, df_cnc: pd.DataFrame, service_choisi: str = "Tous") -> pd.DataFrame:
    if service_choisi != "Tous":
        df_cnd = df_cnd[df_cnd["service"] == service_choisi]
    agg = (
        df_cnd.groupby("id_irm")["sum(distance_km_hp)"]
        .sum()
        .reset_index()
        .rename(columns={"sum(distance_km_hp)": "total_km_hp"})
        .sort_values("total_km_hp", ascending=False)
        .head(11)
    )
    result = _enrich(agg, df_cnc)
    result = result[result["nom_irm"].notna() & (result["nom_irm"] != "")]
    result = result[result["prenom_irm"].notna() & (result["prenom_irm"] != "")]
    result["rang"] = range(1, len(result) + 1)
    return result[["rang", "nom_irm", "prenom_irm", "id_irm", "immatriculation", "total_km_hp"]]

def top10_par_mois(df_cnd: pd.DataFrame, df_cnc: pd.DataFrame, mois_choisi: str, service_choisi: str = "Tous") -> pd.DataFrame:
    df_cnd = df_cnd.copy()
    df_cnd["mois"] = df_cnd["by_date"].dt.to_period("M")
    if service_choisi != "Tous":
        df_cnd = df_cnd[df_cnd["service"] == service_choisi]
    df_mois = df_cnd[df_cnd["mois"] == mois_choisi]
    agg = (
        df_mois.groupby("id_irm")["sum(distance_km_hp)"]
        .sum()
        .reset_index()
        .rename(columns={"sum(distance_km_hp)": "total_km_hp"})
        .sort_values("total_km_hp", ascending=False)
        .head(11)
    )
    result = _enrich(agg, df_cnc)
    result = result[result["nom_irm"].notna() & (result["nom_irm"] != "")]
    result = result[result["prenom_irm"].notna() & (result["prenom_irm"] != "")]
    result["rang"] = range(1, len(result) + 1)
    return result[["rang", "nom_irm", "prenom_irm", "id_irm", "immatriculation", "total_km_hp"]]