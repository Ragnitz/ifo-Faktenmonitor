import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="ifo Faktenmonitor Ostdeutschland - Interaktives Datenportal",
    page_icon="📊",
    layout="wide"
)

# HINWEIS: Hier die beiden echten OneDrive-Direktlinks eintragen (mit download=1)
ONEDRIVE_EXCEL_URL = "https://live.com"
# Ein Freigabelink zu dem Bilderordner auf OneDrive
ONEDRIVE_IMAGES_BASE_URL = "https://live.com"

@st.cache_data
def load_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.ExcelFile(response.content, engine="openpyxl")
    except Exception as e:
        st.error(f"Fehler beim Laden vom OneDrive: {e}")
        return None

with st.spinner("Lade 250 Indikatoren live aus dem ifo OneDrive..."):
    excel_object = load_data(ONEDRIVE_EXCEL_URL)

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
                start_bild_nummer += len(excel_object.book[matching_abb_sheet[0]]._charts)
            except:
                start_bild_nummer += 20
                
    current_charts_count = 20
    current_abb_sheet = [s for s in abbildungsseiten if selected_kapitel in s or s.replace("Abbildung", "").strip() in selected_kapitel]
    if current_abb_sheet:
        try:
            current_charts_count = len(excel_object.book[current_abb_sheet[0]]._charts)
        except:
            pass

    col1, col2 = st.columns(2)
    for i in range(current_charts_count):
        aktuelles_bild = start_bild_nummer + i
        # ERKLÄRUNG: Erzeugt die URL zum Bild direkt im OneDrive-Ordner
        bild_url = f"{ONEDRIVE_IMAGES_BASE_URL}/image{aktuelles_bild:03d}.png"
        
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            # Streamlit lädt das Bild direkt via Internet-Link aus Ihrem OneDrive
            st.image(bild_url, caption=f"Diagramm {i+1} aus dem Bereich {selected_kapitel}", use_container_width=True)
                
    st.markdown("---")
    st.caption("**Datenquelle:** ifo Institut Dresden / Mitteldeutsche Stiftung Wissenschaft und Bildung (c/o VNG AG).")