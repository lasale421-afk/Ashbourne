import streamlit as st
from data_loader import load_data
from compute import top10_global, top10_par_mois
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Fraude Télématique",
    page_icon="🚗",
    layout="wide"
)

# Chargement des données
with st.spinner("Chargement des données depuis GitLab..."):
    try:
        df_cnd = load_data()
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        st.stop()

# Navigation
page = st.sidebar.radio("Navigation", ["🏠 Accueil", "🏆 Top 10 Global", "📅 Top 10 par Mois"])

# Filtres sidebar
st.sidebar.divider()
services = ["Tous"] + sorted(
    df_cnd["service_irm"].dropna().replace("(null)", None).dropna().unique().tolist()
)
service_choisi = st.sidebar.selectbox("Filtrer par service", services)

col1, col2 = st.sidebar.columns([1, 2])
with col1:
    if st.sidebar.button("🔄 Rafraîchir"):
        st.cache_data.clear()
        st.rerun()
with col2:
    st.sidebar.caption(f"MAJ : {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")

dark_mode = st.sidebar.toggle("🌙 Mode sombre", value=False)
if dark_mode:
    st.markdown("""
        <style>
            .stApp { background-color: #0f0f0f; color: #ffffff; }
            section[data-testid="stSidebar"] { background-color: #1a1a1a; }
            .stMarkdown, .stText, p, h1, h2, h3, label { color: #ffffff !important; }
            .stDataFrame { background-color: #1a1a1a; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .stApp { background-color: #ffffff; color: #1a1a1a; }
            section[data-testid="stSidebar"] { background-color: #f5f5f5; }
            .stMarkdown, .stText, p, h1, h2, h3, label { color: #1a1a1a !important; }
        </style>
    """, unsafe_allow_html=True)

# --- ACCUEIL ---
if page == "🏠 Accueil":
    st.title("🚗 Dashboard Fraude Kilométrique")
    st.markdown("""
    Bienvenue sur le dashboard de suivi des distances parcourues **hors journée de travail**.

    ### Navigation
    - **Top 10 Global** : classement tous mois confondus
    - **Top 10 par Mois** : classement filtrable par mois

    ### Filtres disponibles
    - Filtrer par **service** depuis le menu à gauche
    - Rafraîchir les données depuis GitLab
    """)

# --- TOP 10 GLOBAL ---
elif page == "🏆 Top 10 Global":
    st.title("🏆 Top 10 Global")

    df_global = top10_global(df_cnd, service_choisi)
    df_global["total_km_hp"] = df_global["total_km_hp"].round(1)

    # Metric cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total KM HP flotte", f"{df_cnd[df_cnd['is_hp'] == 1]['distance_parcourue_en_km'].sum():,.0f} km")
    with col2:
        st.metric("Conducteurs concernés", df_cnd[df_cnd['is_hp'] == 1]["id_irm"].nunique())
    with col3:
        st.metric("Moyenne KM HP / conducteur", f"{df_cnd[df_cnd['is_hp'] == 1].groupby('id_irm')['distance_parcourue_en_km'].sum().mean():,.0f} km")

    st.divider()

    # Bar chart
    fig = px.bar(
        df_global.sort_values("total_km_hp"),
        x="total_km_hp",
        y=df_global.sort_values("total_km_hp").apply(lambda r: f"{r['prenom_irm']} {r['nom_irm']}", axis=1),
        orientation="h",
        labels={"x": "KM HP", "y": ""},
        color="total_km_hp",
        color_continuous_scale="Reds"
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Tableau
    st.dataframe(df_global, width='stretch', hide_index=True,
        column_config={"total_km_hp": st.column_config.NumberColumn("Total KM HP", format="%.1f km")})

    import io
    col1, col2 = st.columns(2)
    with col1:
        csv = df_global.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export CSV", csv, "top10_global.csv", "text/csv")
    with col2:
        buffer = io.BytesIO()
        df_global.to_excel(buffer, index=False)
        st.download_button("📥 Export Excel", buffer.getvalue(), "top10_global.xlsx", "application/vnd.ms-excel")

# --- TOP 10 PAR MOIS ---
elif page == "📅 Top 10 par Mois":
    st.title("📅 Top 10 par Mois")

    df_cnd_copy = df_cnd.copy()
    df_cnd_copy["mois"] = pd.to_datetime(df_cnd_copy["by_date"]).dt.to_period("M")
    mois_disponibles = sorted(df_cnd_copy["mois"].unique(), reverse=True)
    mois_str = [str(m) for m in mois_disponibles]
    mois_choisi = st.selectbox("Choisir un mois", mois_str)

    df_mois = top10_par_mois(df_cnd, mois_choisi, service_choisi)
    df_mois["total_km_hp"] = df_mois["total_km_hp"].round(1)

    # Metric cards
    df_mois_all = df_cnd_copy[(df_cnd_copy["mois"] == mois_choisi) & (df_cnd_copy["is_hp"] == 1)]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total KM HP ce mois", f"{df_mois_all['distance_parcourue_en_km'].sum():,.0f} km")
    with col2:
        st.metric("Conducteurs concernés", df_mois_all["id_irm"].nunique())
    with col3:
        st.metric("Moyenne KM HP / conducteur", f"{df_mois_all.groupby('id_irm')['distance_parcourue_en_km'].sum().mean():,.0f} km")

    st.divider()

    # Bar chart
    fig = px.bar(
        df_mois.sort_values("total_km_hp"),
        x="total_km_hp",
        y=df_mois.sort_values("total_km_hp").apply(lambda r: f"{r['prenom_irm']} {r['nom_irm']}", axis=1),
        orientation="h",
        labels={"x": "KM HP", "y": ""},
        color="total_km_hp",
        color_continuous_scale="Reds"
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Tableau
    st.dataframe(df_mois, width='stretch', hide_index=True,
        column_config={"total_km_hp": st.column_config.NumberColumn("KM HP", format="%.1f km")})

    import io
    col1, col2 = st.columns(2)
    with col1:
        csv = df_mois.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export CSV", csv, f"top10_{mois_choisi}.csv", "text/csv")
    with col2:
        buffer = io.BytesIO()
        df_mois.to_excel(buffer, index=False)
        st.download_button("📥 Export Excel", buffer.getvalue(), f"top10_{mois_choisi}.xlsx", "application/vnd.ms-excel")