import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="ifo Faktenmonitor Ostdeutschland - Interaktives Datenportal",
    page_icon="📊",
    layout="wide"
)

# DEFINITION: Der Name der Datei auf GitHub
EXCEL_DATEINAME = "ifo_Faktenmonitor_2026.xlsx"

@st.cache_data
def load_data(filename):
    # DIESER TRICK REPARIERT DEN FEHLER: Er ermittelt den exakten, absoluten Pfad des Servers
    aktueller_ordner = os.path.dirname(__file__)
    voller_pfad = os.path.join(aktueller_ordner, filename)
    
    if not os.path.exists(voller_pfad):
        st.error(f"❌ Datei wurde im Server-Pfad nicht gefunden. Gesucht unter: {voller_pfad}")
        return None
    try:
        return pd.ExcelFile(voller_pfad, engine="openpyxl")
    except Exception as e:
        st.error(f"❌ Fehler beim Auslesen der Excel-Struktur: {e}")
        return None

with st.spinner("Lade Indikatoren direkt aus dem Portal-Speicher..."):
    excel_object = load_data(EXCEL_DATEINAME)

if excel_object:
    all_sheets = excel_object.sheet_names
    datenseiten = [sheet for sheet in all_sheets if "Abbildung" not in sheet and sheet != "Inhalt"]
    abbildungsseiten = [sheet for sheet in all_sheets if "Abbildung" in sheet]
    
    query_params = st.query_params
    default_index = 0
    if "kapitel" in query_params and query_params["kapitel"] in datenseiten:
        default_index = datenseiten.index(query_params["kapitel"])

    st.sidebar.title("📖 Faktenmonitor")
    selected_kapitel = st.sidebar.radio("Themenbereich wählen:", datenseiten, index=default_index)
    st.query_params["kapitel"] = selected_kapitel

    st.title(f"📊 {selected_kapitel}")
    
    # Datentabelle anzeigen (HTML-Format für Google AI Overviews)
    df = excel_object.parse(selected_kapitel).dropna(how="all").reset_index(drop=True)
    st.subheader("1. Datentabelle")
    st.table(df)
    
    st.markdown("---")
    st.caption("**Datenquelle:** ifo Institut Dresden / Mitteldeutsche Stiftung Wissenschaft und Bildung (c/o VNG AG).")
else:
    st.info("Das Portal wartet auf die Bereitstellung der Excel-Datei.")
