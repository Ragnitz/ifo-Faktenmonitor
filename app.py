import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="ifo Faktenmonitor Ostdeutschland - Interaktives Datenportal",
    page_icon="📊",
    layout="wide"
)

# DEFINITION: Der Name der Excel-Datei, die Sie gleich bei GitHub hochladen
EXCEL_DATEINAME = "ifo Faktenmonitor_2026.xlsx"

@st.cache_data
def load_data(filename):
    try:
        # Liest die Datei direkt aus dem lokalen GitHub-Verzeichnis
        return pd.ExcelFile(filename, engine="openpyxl")
    except Exception as e:
        st.error(f"Fehler beim Laden der lokalen Excel-Datei: {e}")
        return None

with st.spinner("Lade 250 Indikatoren direkt aus dem Portal-Speicher..."):
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
    
    # Datentabelle anzeigen (HTML für Google-KI)
    df = excel_object.parse(selected_kapitel).dropna(how="all").reset_index(drop=True)
    st.subheader("1. Datentabelle")
    st.table(df)
    
    st.markdown("---")
    st.subheader("2. Zugehörige Abbildungen")
    
    # Startnummer berechnen
    kapitel_index = datenseiten.index(selected_kapitel)
    start_bild_nummer = 1
    for idx in range(kapitel_index):
        prev_kapitel = datenseiten[idx]
        matching_abb_sheet = [s for s in abbildungsseiten if prev_kapitel in s or s.replace("Abbildung", "").strip() in prev_kapitel]
        if matching_abb_sheet:
            try:
                start_bild_nummer += len(excel_object.book[matching_abb_sheet]._charts)
            except:
                start_bild_nummer += 20
                
    current_charts_count = 20
    current_abb_sheet = [s for s in abbildungsseiten if selected_kapitel in s or s.replace("Abbildung", "").strip() in selected_kapitel]
    if current_abb_sheet:
        try:
            current_charts_count = len(excel_object.book[current_abb_sheet]._charts)
        except:
            pass

    col1, col2 = st.columns(2)
    for i in range(current_charts_count):
        aktuelles_bild = start_bild_nummer + i
        dateiname = f"images/image{aktuelles_bild:03d}.png"
        
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            try:
                st.image(dateiname, caption=f"Diagramm {i+1} aus dem Bereich {selected_kapitel}", use_container_width=True)
            except:
                pass
                
    st.markdown("---")
    st.caption("**Datenquelle:** ifo Institut Dresden / Mitteldeutsche Stiftung Wissenschaft und Bildung (c/o VNG AG).")
else:
    st.info(f"Bitte stellen Sie sicher, dass die Datei '{EXCEL_DATEINAME}' auf GitHub hochgeladen wurde.")
