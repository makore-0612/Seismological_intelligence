import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PROF_MAP = {'Superficial': 0, 'Intermedio': 1, 'Profundo': 2, 'Desconocida': 3}

FEATURES_24H = [
    'magnitud', 'profundidad', 'latitud', 'longitud', 'prof_cod',
    'hora_local', 'Mc_epoca', 'n_replicas_1h', 'mag_max_1h', 'tasa_1h',
    'omori_pred_24h',
]
FEATURES_MAG = [
    'magnitud', 'profundidad', 'latitud', 'longitud', 'prof_cod',
    'hora_local', 'Mc_epoca', 'n_replicas_1h', 'mag_max_1h', 'tasa_1h',
]


@st.cache_data
def load_catalog():
    df = pd.read_parquet(BASE_DIR / 'seismos_clean.parquet')
    df = df.rename(columns={'Latitud': 'latitud', 'Longitud': 'longitud',
                             'Profundidad': 'profundidad'})
    df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])
    df['momento_sismico'] = 10 ** (1.5 * df['Magnitud'])
    conditions = [df['profundidad'].isna(), df['profundidad'] < 70, df['profundidad'] < 300]
    df['categoria_prof'] = np.select(conditions,
                                     ['Desconocida', 'Superficial', 'Intermedio'],
                                     default='Profundo')
    return df


@st.cache_data
def load_mainshocks():
    ms = pd.read_parquet(BASE_DIR / 'mainshocks.parquet')
    ms['datetime_utc'] = pd.to_datetime(ms['datetime_utc'])
    ms['mag_max_1h'] = ms['mag_max_1h'].fillna(0)
    ms['prof_cod'] = ms['categoria_prof'].map(PROF_MAP).fillna(-1).astype(int)
    return ms


@st.cache_data
def load_replicas():
    rep = pd.read_parquet(BASE_DIR / 'replicas.parquet')
    rep['datetime_utc'] = pd.to_datetime(rep['datetime_utc'])
    return rep


@st.cache_data
def load_omori():
    return pd.read_parquet(BASE_DIR / 'omori_params.parquet')


@st.cache_data
def load_agg_anual():
    return pd.read_parquet(BASE_DIR / 'agg_anual.parquet')


@st.cache_data
def load_agg_hora():
    return pd.read_parquet(BASE_DIR / 'agg_hora.parquet')


@st.cache_resource
def load_model_24h():
    return joblib.load(BASE_DIR / 'modelo_mejor_24h.joblib')


@st.cache_resource
def load_model_mag48h():
    return joblib.load(BASE_DIR / 'modelo_mejor_mag48h.joblib')
