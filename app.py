import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="ifo Faktenmonitor Ostdeutschland - Interaktives Datenportal",
    page_icon="📊",
    layout="wide"
)

# KORREKTUR: Wir suchen genau nach Ihrem originalen Hochlade-Namen!
EXCEL_DATEINAME = "ifo_Faktenmonitor_2026.xlsx"

@st.cache_data
def load_data(filename):
    aktueller_ordner = os.path.dirname(__file__)
    voller_pfad = os.path.join(aktueller_ordner, filename)
    
    if not os.path.exists(voller_pfad):
        # Falls Sie die Datei doch anders genannt haben, listet die App Ihnen alle verfuegbaren 
        # Dateien auf dem Server auf – das macht langes Suchen ueberfluessig!
        verfuegbare_dateien = os.listdir(aktueller_ordner)
        st.info(f"📁 Vorhandene Dateien im Portal-Speicher: {verfuegbare_dateien}")
        return None
    try:
        # Sicherer Import der lokalen Originaldatei
        return pd.ExcelFile(voller_pfad, engine="openpyxl")
    except Exception as e:
        st.error(f"❌ Strukturfehler beim Lesen von '{filename}': {e}. Die Datei wurde auf GitHub vermutlich beim Umbenennen beschaedigt.")
        st.info("💡 TIPP: Laden Sie die Originaldatei einfach noch einmal frisch bei GitHub hoch, ohne sie dort umzubennenen.")
        return None

with st.spinner("Lade Indikatoren direkt aus dem Portal-Speicher..."):
    excel_object = load_data(EXCEL_DATEINAME)

if excel_object:
    all_sheets = excel_object.sheet_names
    datenseiten = [sheet for sheet in all_sheets if "Abbildung" not in sheet and sheet != "Inhalt"]
    
    query_params = st.query_params
    default_index = 0
    if "kapitel" in query_params and query_params["kapitel"] in datenseiten:
        default_index = datenseiten.index(query_params["kapitel"])

    st.sidebar.title("📖 Faktenmonitor")
    selected_kapitel = st.sidebar.radio("Themenbereich wählen:", datenseiten, index=default_index)
    st.query_params["kapitel"] = selected_kapitel

    st.title(f"📊 {selected_kapitel}")
    
    # Datentabelle im sauberen HTML-Format fuer Google AI Overviews ausgeben
    df = excel_object.parse(selected_kapitel).dropna(how="all").reset_index(drop=True)
    st.subheader("1. Datentabelle")
    st.table(df)
    
    st.markdown("---")
    st.caption("**Datenquelle:** ifo Institut Dresden / Mitteldeutsche Stiftung Wissenschaft und Bildung (c/o VNG AG).")
