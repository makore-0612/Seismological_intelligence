import sys
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent

RUTA_IMAGEN = BASE_DIR / "assets" / "logo.png"

icono = Image.open(RUTA_IMAGEN)

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

from utils.loaders import load_catalog
from utils.footer import render_footer


st.set_page_config(page_title="Sismicidad Histórica", page_icon=icono, layout="wide")
st.title("Sismicidad Histórica")

catalog = load_catalog()

# --- Sidebar ---
with st.sidebar:
    st.header("Filtros")
    year_min = int(catalog['year'].min())
    year_max = int(catalog['year'].max())
    mag_inf = float(catalog['Magnitud'].min())
    mag_sup = float(catalog['Magnitud'].max())
    year_range = st.slider("Rango de años", year_min, year_max, (2000, year_max))
    mag_min = st.slider("Magnitud mínima", mag_inf, mag_sup, 4.0, step=0.1)
    prof_opts = ['Todas', 'Superficial', 'Intermedio', 'Profundo']
    prof_sel = st.selectbox("Profundidad", prof_opts)
    solo_mc = st.checkbox("Solo eventos sobre Mc", value=True)

# --- Filter ---
with st.spinner("⏳ Cargando y filtrando el catálogo del SSN..."):
    df = catalog[
        (catalog['year'] >= year_range[0]) &
        (catalog['year'] <= year_range[1]) &
        (catalog['Magnitud'] >= mag_min)
    ].copy()
    if prof_sel != 'Todas':
        df = df[df['categoria_prof'] == prof_sel]
    if solo_mc:
        df = df[df['sobre_Mc']]

# --- KPI cards ---
c1, c2, c3, c4 = st.columns(4)

# KPI 1: Eventos
with c1:
    with st.container(border=True):
        st.metric(
            label="Eventos", 
            value=f"{len(df):,}"
        )

# KPI 2: Magnitud máxima
with c2:
    with st.container(border=True):
        val_max = f"{df['Magnitud'].max():.1f}" if len(df) else "-"
        st.metric(
            label="Magnitud máxima", 
            value=val_max
        )

# KPI 3: Magnitud media
with c3:
    with st.container(border=True):
        val_mean = f"{df['Magnitud'].mean():.2f}" if len(df) else "-"
        st.metric(
            label="Magnitud media", 
            value=val_mean
        )

# KPI 4: Prof. media (km)
with c4:
    with st.container(border=True):
        val_prof = f"{df['profundidad'].mean():.0f}" if len(df) else "-"
        st.metric(
            label="Prof. media (km)", 
            value=val_prof
        )

# --- Heatmap ---
st.subheader("Energía sísmica acumulada")

with st.spinner("⏳ Cargando y filtrando el catálogo del SSN..."):
    grilla = (
        df.assign(
            lat_bin=(df['latitud'] / 0.5).round() * 0.5,
            lon_bin=(df['longitud'] / 0.5).round() * 0.5,
        )
        .groupby(['lat_bin', 'lon_bin'])['momento_sismico']
        .sum()
        .reset_index()
    )

    m = folium.Map(location=[22, -102], zoom_start=5, tiles='CartoDB dark_matter')
    if len(grilla) > 0:
        max_val = grilla['momento_sismico'].quantile(0.98)
        heat_data = grilla[['lat_bin', 'lon_bin', 'momento_sismico']].values.tolist()
        HeatMap(heat_data, radius=14, blur=18, max_zoom=1,
                min_opacity=0.3, max_val=max_val).add_to(m)

    st_folium(m, width=None, height=500, returned_objects=[])

# --- Serie temporal ---
st.subheader("Actividad anual")
st.caption("Es importante mencionar: No es que haya más actividad sismológica con el pasar de los años, sino que nuestra capacidad de detectar sismos ha ido mejorando. Los años recientes con menos registros se deben a errores o mantenimiento en los sensores.")

anual = (
    df.groupby('year')
    .agg(n_sismos=('Magnitud', 'count'), mag_media=('Magnitud', 'mean'))
    .reset_index()
)

fig = px.bar(
    anual, x='year', y='n_sismos',
    color='mag_media',
    color_continuous_scale='YlOrRd',
    labels={'year': 'Año', 'n_sismos': 'N° eventos', 'mag_media': 'Mag. media'},
    template='plotly_dark',
)
fig.update_layout(coloraxis_colorbar_title='Mag.<br>media')
st.plotly_chart(fig, use_container_width=True)

# --- Top 10 ---
st.subheader("Eventos más grandes en el período")
if len(df) > 0:
    top = (
        df.nlargest(10, 'Magnitud')
        [['datetime_utc', 'Magnitud', 'profundidad', 'latitud', 'longitud', 'estado']]
        .copy()
    )
    top['datetime_utc'] = top['datetime_utc'].dt.strftime('%Y-%m-%d %H:%M')
    top.columns = ['Fecha UTC', 'Magnitud', 'Prof. (km)', 'Lat', 'Lon', 'Estado']
    st.dataframe(top, use_container_width=True, hide_index=True)
else:
    st.info("Sin eventos con los filtros actuales.")

render_footer()
