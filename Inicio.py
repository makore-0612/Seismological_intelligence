from pathlib import Path
from PIL import Image
import streamlit as st
from utils.footer import render_footer

BASE_DIR = Path(__file__).resolve().parent

icono = Image.open(BASE_DIR / "assets" / "logo.png")

geo = BASE_DIR / "assets" / "geofisica.png"

unam = BASE_DIR / "assets" / "unam.png"

st.set_page_config(
    page_title="Inteligencia Sismológica MX",
    page_icon=icono, 
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stColumns"] {
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([0.1, 0.9])

with col1:
    st.image(str(BASE_DIR / "assets" / "logo.png"), width=80) # Convertimos a str por compatibilidad con st.image
with col2:
    st.title("Inteligencia Sismológica – México")

st.caption("Catálogo SSN/UNAM desde 1974 hasta 2026: **368 000+ eventos**")

st.markdown("""
El estudio de la sismicidad en México representa un desafío crítico y de vital importancia. Ante la imposibilidad física de predecir estos fenómenos, el análisis de datos históricos se convierte en nuestra mejor herramienta para comprender su impacto en territorio nacional.

Utilizando los registros oficiales del Servicio Sismológico Nacional (SSN), esta aplicación ofrece un entorno de visualización y modelado para estudiar el comportamiento de estos movimientos. Te invitamos a explorar los siguientes módulos:
""")

col1, col2, col3 = st.columns(3)

with col1:
    # El texto usa \n para darles un formato similar
    texto_1 = "**Sismicidad histórica**\n\nEnergía sísmica con filtros por año, magnitud y profundidad."
    if st.button(texto_1, use_container_width=True, key="btn_sismicidad"):
        st.switch_page("pages/1_Sismicidad_Historica.py")  

with col2:
    texto_2 = "**Profundidad**\n\nPerfil de subducción, distribución regional de sismos y actividad horaria."
    if st.button(texto_2, use_container_width=True, key="btn_profundidad"):
        st.switch_page("pages/2_Profundidad.py")

with col3:
    texto_3 = "**Simulador de réplicas**\n\nPredicción ML de réplicas en 24h y magnitud máxima en 48h para eventos."
    if st.button(texto_3, use_container_width=True, key="btn_replicas"):
        st.switch_page("pages/3_Simulador.py")

st.divider()
st.markdown("""
>**Fuente de datos:** [Servicio Sismológico Nacional — UNAM](http://www.ssn.unam.mx/)
""")

with st.container(horizontal_alignment='center'):
    st.image(str(geo), width = 120) 

render_footer()
