import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="ifo Faktenmonitor Ostdeutschland - Interaktives Datenportal",
    page_icon="📊",
    layout="wide"
)

# HINWEIS: Hier Ihren echten OneDrive-Direktlink eintragen
ONEDRIVE_DIRECT_URL = "C:\Users\Ragnitz\OneDrive - ifo Institut\VGR-Daten\ifo Faktenmonitor_2026.xlsm"

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
    excel_object = load_data(ONEDRIVE_DIRECT_URL)

if excel_object:
    # 1. Alle Tabellenblaetter auslesen und trennen
    all_sheets = excel_object.sheet_names
    datenseiten = [sheet for sheet in all_sheets if "Abbildung" not in sheet and sheet != "Inhalt"]
    abbildungsseiten = [sheet for sheet in all_sheets if "Abbildung" in sheet]
    
    # Navigation und Deep-Linking für Google AI Overviews
    query_params = st.query_params
    default_index = 0
    if "kapitel" in query_params and query_params["kapitel"] in datenseiten:
        default_index = datenseiten.index(query_params["kapitel"])

    st.sidebar.title("📖 Faktenmonitor")
    selected_kapitel = st.sidebar.radio("Themenbereich wählen:", datenseiten, index=default_index)
    st.query_params["kapitel"] = selected_kapitel

    st.title(f"📊 {selected_kapitel}")
    st.markdown(f"Hier sehen Sie die Strukturdaten des *ifo Faktenmonitors* zum Bereich **{selected_kapitel}**.")
    
    # 2. Datentabelle einlesen und anzeigen (HTML für Google-KI)
    df = excel_object.parse(selected_kapitel).dropna(how="all").reset_index(drop=True)
    st.subheader("1. Datentabelle")
    st.table(df)
    
    # --- NEUE FLEXIBLE BILDER-LOGIK (Egal wie viele Bilder pro Blatt existieren) ---
    st.markdown("---")
    st.subheader("2. Zugehörige Abbildungen")
    
    # Wir zaehlen im Hintergrund zusammen, wie viele Bilder VOR diesem Kapitel liegen
    kapitel_index = datenseiten.index(selected_kapitel)
    start_bild_nummer = 1
    
    for idx in range(kapitel_index):
        prev_kapitel = datenseiten[idx]
        # Wir suchen das passende Abbildungsblatt in Excel (z.B. "Abbildung_Wirtschaftskraft")
        matching_abb_sheet = [s for s in abbildungsseiten if prev_kapitel in s or s.replace("Abbildung", "").strip() in prev_kapitel]
        if matching_abb_sheet:
            try:
                # Wir zaehlen live, wie viele Diagramme auf diesem vorherigen Blatt lagen
                prev_df = excel_object.parse(matching_abb_sheet[0])
                # Openpyxl zaehlt die enthaltenen Chart-Objekte auf dem Blatt
                num_charts = len(excel_object.book[matching_abb_sheet[0]]._charts)
                start_bild_nummer += num_charts
            except:
                start_bild_nummer += 20 # Sicherheits-Fallback falls das Auslesen fehlschlaegt
                
    # Jetzt ermitteln wir, wie viele Bilder das AKTUELLE Kapitel hat
    current_charts_count = 20 # Standard-Wert falls keine genaue Zuordnung moeglich ist
    current_abb_sheet = [s for s in abbildungsseiten if selected_kapitel in s or s.replace("Abbildung", "").strip() in selected_kapitel]
    if current_abb_sheet:
        try:
            current_charts_count = len(excel_object.book[current_abb_sheet[0]]._charts)
        except:
            pass

    # Bilder in einer eleganten 2-Spalten-Struktur ausgeben
    col1, col2 = st.columns(2)
    
    for i in range(current_charts_count):
        aktuelles_bild = start_bild_nummer + i
        dateiname = f"images/image{aktuelles_bild:03d}.png" # Generiert z.B. images/image042.png
        
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            try:
                st.image(dateiname, caption=f"Diagramm {i+1} aus dem Bereich {selected_kapitel}", use_container_width=True)
            except:
                pass
                
    st.markdown("---")
    st.caption("**Datenquelle:** ifo Institut Dresden / Mitteldeutsche Stiftung Wissenschaft und Bildung (c/o VNG AG).")
else:
    st.info("Warte auf korrekten OneDrive-Link.")
