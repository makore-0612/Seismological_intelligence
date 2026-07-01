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
import plotly.graph_objects as go

from utils.loaders import (
    load_mainshocks, load_replicas, load_omori,
    load_model_24h, load_model_mag48h,
    FEATURES_24H, FEATURES_MAG,
)
from utils.footer import render_footer


st.set_page_config(page_title="Simulador de Réplicas", page_icon=icono, layout="wide")
st.title("Simulador de Réplicas")
st.markdown(r"""
Por excelencia, para estimar la cantidad de réplicas después de un movimiento telúrico significativo se usa la **Ley de Omori modificada** (Utsu, 1961), que describe la tasa de réplicas como:""")

st.latex(r"""\lambda(t) = \frac{K}{(t + c)^p}""")

st.markdown(r"""donde $t$ es el tiempo en horas desde el sismo principal, $K$ es la productividad, $c$ evita la singularidad en $t=0$ y $p$ controla la velocidad de decaimiento.

El número esperado de réplicas en $[t_1, t_2]$ es:""")

st.latex(r"""N(t_1, t_2) = \int_{t_1}^{t_2} \lambda(t)\, dt = \frac{K}{1-p}\left[(t_2+c)^{1-p} - (t_1+c)^{1-p}\right] \quad (p \neq 1)""")

st.markdown(r"""Pese a que es aceptado ampliamente en la literatura, surgen dos preguntas en particular: ¿Existirá otro método para estimar el número de réplicas?, ¿Qué magnitud llegarán a tener?
""")
st.caption("Selecciona un sismo principal del catálogo a la izquierda para obtener predicciones ML.")

# --- Load data ---
mainshocks = load_mainshocks()
replicas = load_replicas()
omori = load_omori()
model_24h = load_model_24h()
model_mag = load_model_mag48h()

# --- Sidebar selector ---
with st.sidebar:
    st.header("Selección de evento")
    ms_sorted = mainshocks.sort_values('datetime_utc', ascending=False)
    labels = [
        f"{row.datetime_utc.strftime('%Y-%m-%d')}  M{row.magnitud:.1f}  {row.estado}"
        for row in ms_sorted.itertuples()
    ]
    idx = st.selectbox("Sismo principal", range(len(labels)), format_func=lambda i: labels[i])
    selected = ms_sorted.iloc[idx]

# --- Event info ---
st.subheader("Información del evento")
c1, c2, c3, c4 = st.columns([0.35, 0.15, 0.35, 0.15])
with c1:
    with st.container(border=True):
        st.metric(
            label="Fecha UTC", 
            value=selected['datetime_utc'].strftime('%Y-%m-%d %H:%M')
        )

with c2:
    with st.container(border=True):
        st.metric(
            label="Magnitud", 
            value=f"M {selected['magnitud']:.1f}"
        )

with c3:
    with st.container(border=True):
        st.metric(
            label="Profundidad", 
            value= f"{selected['profundidad']:.0f} km  ({str(selected['categoria_prof'])[:6]}.)"
        )

with c4:
    with st.container(border=True):
        st.metric(
            label="Estado", 
            value= selected['estado'] if pd.notna(selected['estado']) else "—"
        )

st.divider()

# --- Omori params for this event ---
ms_id = int(selected['mainshock_id'])
omori_row = omori[omori['mainshock_id'] == ms_id]
has_omori = len(omori_row) > 0 and pd.notna(omori_row.iloc[0]['K'])

if has_omori:
    K = float(omori_row.iloc[0]['K'])
    c_p = float(omori_row.iloc[0]['c'])
    p = float(omori_row.iloc[0]['p'])
    T_obs = float(omori_row.iloc[0]['T_obs_horas'])
    omori_pred_24h = float(omori_row.iloc[0]['omori_pred_24h'])
else:
    omori_pred_24h = 0.0

# --- Build feature vector ---
row_feat = {
    'magnitud': selected['magnitud'],
    'profundidad': selected['profundidad'],
    'latitud': selected['latitud'],
    'longitud': selected['longitud'],
    'prof_cod': int(selected['prof_cod']),
    'hora_local': int(selected['hora_local']),
    'Mc_epoca': float(selected['Mc_epoca']),
    'n_replicas_1h': float(selected['n_replicas_1h']),
    'mag_max_1h': float(selected['mag_max_1h']),
    'tasa_1h': float(selected['tasa_1h']),
    'omori_pred_24h': omori_pred_24h,
}

X_24h = pd.DataFrame([row_feat])[FEATURES_24H]
X_mag = pd.DataFrame([row_feat])[FEATURES_MAG]

pred_24h = float(np.maximum(model_24h.predict(X_24h)[0], 0))
pred_mag  = float(np.maximum(model_mag.predict(X_mag)[0], 0))

# Real values (from catalog)
real_24h = int(selected['n_replicas_24h'])
real_mag  = selected['mag_max_48h']

# --- ML Predictions ---
col_ml, col_chart = st.columns([1, 2])

with col_ml:
    st.subheader("Predicciones ML")

    st.markdown("**Réplicas esperadas en 24h**")
    st.caption(">**Modelo:** XGBoost apoyado en la Ley de Omori (Cálculo de réplicas en 24H, $R^2=0.41$)")
    p1, p2, p3 = st.columns(3)
    p1.metric("Omori (base)", f"{omori_pred_24h:.1f}")
    p2.metric("XGB con Omori", f"{pred_24h:.1f}")
    p3.metric("Real", f"{real_24h}")

    st.markdown("**Magnitud máxima esperada en 48h**")
    st.caption(">**Modelo:** Random Forest (Magnitud de réplica máxima en 48H, $R^2=0.33$)")
    p4, p5 = st.columns(2)
    p4.metric("Predicción", f"M {pred_mag:.2f}")
    if pd.notna(real_mag) and real_mag > 0:
        p5.metric("Real", f"M {real_mag:.2f}")
    else:
        p5.metric("Real", "Sin réplicas")

    st.divider()
    st.markdown("**Primera hora de actividad**")
    e1, e2, e3 = st.columns(3)
    e1.metric("Réplicas 1h", int(selected['n_replicas_1h']))
    e2.metric("Mag. máx. 1h", f"{selected['mag_max_1h']:.1f}" if selected['mag_max_1h'] > 0 else "—")
    e3.metric("Tasa 1h", f"{selected['tasa_1h']:.2f}/h")

with col_chart:
    st.subheader("Curva de Omori — tasa de réplicas")

    if has_omori:
        # Aftershocks of this event
        reps_ev = replicas[replicas['mainshock_id'] == ms_id].sort_values('dt_horas')
        T_plot = min(T_obs, 7 * 24)  # up to 7 days

        t = np.linspace(0.01, T_plot, 800)
        rate = K / (t + c_p) ** p

        def omori_cum(t_arr, K, c, p):
            if abs(p - 1.0) < 1e-6:
                return K * np.log((t_arr + c) / c)
            return K / (1 - p) * ((t_arr + c) ** (1 - p) - c ** (1 - p))

        cum_expected = omori_cum(t, K, c_p, p)

        fig = go.Figure()

        # Omori rate (secondary y)
        fig.add_trace(go.Scatter(
            x=t, y=rate,
            name='Tasa Omori λ(t)',
            line=dict(color='#90caf9', width=1.5, dash='dot'),
            yaxis='y2', opacity=0.7,
        ))

        # Omori cumulative
        fig.add_trace(go.Scatter(
            x=t, y=cum_expected,
            name='Acumulado Omori',
            line=dict(color='#42a5f5', width=2),
        ))

        # Actual aftershocks cumulative
        if len(reps_ev) > 0:
            times_a = reps_ev['dt_horas'].values
            mask = times_a <= T_plot
            t_a = times_a[mask]
            c_a = np.arange(1, mask.sum() + 1)
            fig.add_trace(go.Scatter(
                x=t_a, y=c_a,
                name='Réplicas reales',
                mode='markers+lines',
                marker=dict(size=4, color='#ef5350'),
                line=dict(color='#ef5350', width=1),
            ))

        # 24h marker
        fig.add_vline(x=24, line_dash='dash', line_color='#ffd54f',
                      annotation_text='24h', annotation_position='top right')

        fig.update_layout(
            template='plotly_dark',
            xaxis_title='Horas desde el sismo principal',
            yaxis_title='Réplicas acumuladas',
            yaxis2=dict(title='Tasa λ(t) [réplicas/h]',
                        overlaying='y', side='right', showgrid=False),
            legend=dict(orientation='h', y=-0.2),
            height=590,
            margin=dict(t=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay parámetros de Omori para este evento (menos de 2 réplicas en el período de observación).")

# --- Aftershock table ---
st.divider()
reps_all = replicas[replicas['mainshock_id'] == ms_id].sort_values('dt_horas')
if len(reps_all) > 0:
    st.subheader(f"Réplicas registradas — {len(reps_all)} eventos")
    show = reps_all[['datetime_utc', 'Magnitud', 'dt_horas', 'dist_km', 'Profundidad']].copy()
    show['datetime_utc'] = show['datetime_utc'].dt.strftime('%Y-%m-%d %H:%M')
    show['dt_horas'] = show['dt_horas'].round(1)
    show['dist_km']  = show['dist_km'].round(1)
    show.columns = ['Fecha UTC', 'Magnitud', 'Δt (h)', 'Dist. (km)', 'Prof. (km)']
    st.dataframe(show.head(200), use_container_width=True, hide_index=True)
else:
    st.info("Este evento no tiene réplicas registradas en el catálogo.")

render_footer()
