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

from utils.loaders import load_catalog, load_agg_hora
from utils.footer import render_footer

st.set_page_config(page_title="Análisis de Profundidad", page_icon=icono, layout="wide")
st.title("Análisis de Profundidad")
st.markdown(""" Para tener mayor distinción entre los eventos, los dividimos en tres categorías:\\
    \t 1. Superficial: Para profundidades menores a 70 km. \\
    \t 2. Intermedio: Profundidades menores a 300 km \\
    \t 3. Profundo: Mayores a 300 km \\
            """)

catalog = load_catalog()
agg_hora = load_agg_hora()

df = catalog[catalog['sobre_Mc']].copy()

df['region'] = pd.cut(
    df['latitud'],
    bins=[13.5, 18, 22, 33.5],
    labels=['Sur (<18°N)', 'Centro (18–22°N)', 'Norte (>22°N)'],
)

# --- Perfil de subducción | Histograma ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Perfil de subducción")
    st.caption("Banda -99° a -95°W (margen Pacífico central)")
    sub = df[(df['longitud'] >= -99) & (df['longitud'] <= -95)].copy()
    if len(sub) > 8000:
        sub = sub.sample(8000, random_state=42)
    fig = px.scatter(
        sub, x='latitud', y='profundidad',
        color='Magnitud',
        color_continuous_scale='magma',
        opacity=0.5,
        size_max=6,
        labels={'latitud': 'Latitud (°N)', 'profundidad': 'Profundidad (km)', 'Magnitud': 'Mag.'},
        template='plotly_dark',
    )
    fig.update_yaxes(autorange='reversed', title='Profundidad (km)')
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribución de profundidad por región")
    fig = px.histogram(
        df.dropna(subset=['region']),
        x='profundidad', color='region',
        nbins=60, barmode='overlay', opacity=0.75,
        labels={'profundidad': 'Profundidad (km)', 'region': 'Región'},
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=420, legend=dict(orientation='h', y=1.05))
    st.plotly_chart(fig, use_container_width=True)

# --- Heatmap hora × magnitud ---
st.subheader("Actividad por hora del día")
st.caption("No existe correlación hora - número de sismos. Sin embargo, empírcamente, hay una mayor cantdad de microsismos en la madrugada. Pese a que puede deberse a errores de medición, no es mala idea tener zapatos junto a la cama.")

hora_mag = (
    df.assign(
        mag_bin=pd.cut(
            df['Magnitud'],
            bins=[3, 4, 5, 6, 7, 9],
            labels=['3–4', '4–5', '5–6', '6–7', '7+'],
        )
    )
    .groupby(['hora_local', 'mag_bin'], observed=True)
    .size()
    .reset_index(name='n')
)

fig = px.density_heatmap(
    hora_mag, x='hora_local', y='mag_bin', z='n',
    color_continuous_scale='Oryel',
    labels={'hora_local': 'Hora local', 'mag_bin': 'Magnitud', 'n': 'Conteo'},
    template='plotly_dark',
)
fig.update_xaxes(dtick=2, title='Hora local (0–23)')
fig.update_yaxes(title='Rango de magnitud')
st.plotly_chart(fig, use_container_width=True)

# --- Stats por categoría de profundidad ---
st.subheader("Resumen por categoría de profundidad")
resumen = (
    df.groupby('categoria_prof')
    .agg(
        n_eventos=('Magnitud', 'count'),
        mag_media=('Magnitud', 'mean'),
        mag_max=('Magnitud', 'max'),
        prof_media=('profundidad', 'mean'),
    )
    .round(2)
    .reset_index()
)
resumen.columns = ['Categoría', 'N° eventos', 'Mag. media', 'Mag. máx.', 'Prof. media (km)']
st.dataframe(resumen, use_container_width=True, hide_index=True)

render_footer()
