# Inteligencia Sismológica — México

Panel interactivo de análisis sísmico e inteligencia artificial para el territorio mexicano, construido sobre el catálogo histórico del Servicio Sismológico Nacional (SSN/UNAM).

---

## Demo

> Disponible en [*Streamlit Community Cloud*](https://seismologicalintelligence.streamlit.app/)

---

## ¿Qué hace este proyecto?

- Visualiza más de **368 000 sismos** registrados en México entre 1974 y 2026
- Estima la magnitud de completitud (Mc) variable por época para filtrar el catálogo de forma estadísticamente válida
- Identifica sismos principales y réplicas mediante el método de declustering de Gardner-Knopoff
- Ajusta la ley de Omori modificada por secuencia (parámetros K, c, p) como línea base física
- Entrena modelos de **Machine Learning** (XGBoost + Random Forest) para predecir réplicas en 24h y magnitud máxima en 48h
- Ofrece un dashboard interactivo con mapa de calor de energía sísmica, análisis de profundidad y simulador de réplicas

---

## Estructura del proyecto

```
├── app.py                        # Entry point del dashboard
├── pages/
│   ├── 1_Sismicidad_Historica.py # Mapa de calor + serie temporal + filtros
│   ├── 2_Profundidad.py          # Perfil de subducción + distribución regional
│   └── 3_Simulador.py            # Predicción ML para eventos del catálogo
├── utils/
│   └── loaders.py                # Carga de datos con caché de Streamlit
├── etapa1_limpieza.ipynb         # Limpieza y estimación de Mc por época
├── etapa2_eda.ipynb              # Análisis exploratorio espacial y temporal
├── etapa3_replicas.ipynb         # Declustering G-K y catálogo de réplicas
├── etapa4_omori.ipynb            # Ajuste de ley de Omori por MLE
├── etapa5_ml.ipynb               # Modelos ML con validación temporal
├── requirements.txt
```

---

## Modelos de Machine Learning

La validación usa bloques temporales cronológicos (5 bloques, entrenamiento en pasado → evaluación en futuro). Nunca split aleatorio.

| Target | Modelo | R² (out-of-sample) | MAE |
|---|---|---|---|
| Réplicas en 24h | XGBoost + Omori (feature) | **0.41** | 6.3 |
| Magnitud máxima en 48h | Random Forest | **0.33** | 1.34 |

El modelo de 24h usa la predicción de Omori como feature adicional, lo que permite al XGBoost anclar su estimación en la física de la secuencia.

---

## Datos

**Fuente:** [Servicio Sismológico Nacional — Instituto de Geofísica, UNAM](http://www.ssn.unam.mx/)

- Rango temporal: 1974–2026 (filtrado por año de red suficientemente densa)
- Umbral de análisis: M ≥ 5.5 para sismos principales
- Magnitud de completitud: variable por época (3.4–3.9, método de máxima curvatura)
- Declustering: Gardner-Knopoff con parámetros relajados (MAX\_TIME=365d, MAX\_DIST=500km, ΔMAG=0.5)

---

## Correr localmente

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd Seismological_intelligence

# Instalar dependencias
pip install -r requirements.txt

# Lanzar el dashboard
streamlit run app.py
```

Requiere **Python 3.12+**.

---

## Stack tecnológico

| Categoría | Herramientas |
|---|---|
| Datos | pandas, numpy, pyarrow |
| Visualización | Plotly, Folium, streamlit-folium |
| ML | XGBoost, scikit-learn |
| Dashboard | Streamlit |
| Deployment | Streamlit Community Cloud |

---

## Autor

**Angel Zamora** — [angeljza0612@gmail.com](mailto:angeljza0612@gmail.com)
