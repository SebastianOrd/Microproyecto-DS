import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# Configuración inicial
API_URL = "https://acceptable-amazement-production.up.railway.app/api/v1/predict"

st.set_page_config(
    page_title="Dashboard de Calidad del Aire",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Dashboard de Calidad del Aire")
st.markdown("Sube tu archivo CSV para analizar datos históricos y generar predicciones.")

# ============================
# Valores por defecto
# ============================
DEFAULT_MUNICIPIOS = ["Dosquebradas", "La Virginia", "Pereira", "Santa Rosa de Cabal"]
DEFAULT_ESTACIONES = ["Balalaika", "Centro", "Centro Urbano", "Cuenca Rio Risaralda"]

# Carga de CSV
file = st.file_uploader("Elige un archivo CSV", type=["csv"])
df = None
if file is not None:
    df = pd.read_csv(file, encoding='utf-8-sig', decimal=',')
    df.columns = df.columns.str.strip()
    df.rename(columns={"Medicion": "PM10", "AÃ±o": "Año"}, inplace=True)
    df["PM10"] = pd.to_numeric(df["PM10"], errors='coerce')
    df = df.dropna(subset=["PM10"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

# Crear pestañas SIEMPRE
tab1, tab2 = st.tabs(["Histórico", "Predicciones"])

# ============================
# PESTAÑA 1: HISTÓRICO
# ============================
with tab1:
    if df is None:
        st.info("🔹 Sube un archivo CSV para ver los datos históricos.")
    else:
        st.subheader("📈 Datos Históricos")

        municipios_hist = st.sidebar.multiselect(
            "Municipio (Histórico):",
            options=sorted(df["Municipio"].dropna().unique()),
            default=sorted(df["Municipio"].dropna().unique())
        )
        estaciones_hist = st.sidebar.multiselect(
            "Estación (Histórico):",
            options=sorted(df["Estacion"].dropna().unique()),
            default=sorted(df["Estacion"].dropna().unique())
        )
        fecha_rango_hist = st.sidebar.date_input(
            "Rango de fechas (Histórico):",
            value=[df["Fecha"].min(), df["Fecha"].max()] if not df["Fecha"].isnull().all() else [datetime(2019,2,1), datetime(2023,2,2)]
        )

        df_hist = df.copy()
        if municipios_hist:
            df_hist = df_hist[df_hist["Municipio"].isin(municipios_hist)]
        if estaciones_hist:
            df_hist = df_hist[df_hist["Estacion"].isin(estaciones_hist)]
        if len(fecha_rango_hist) == 2:
            start_date, end_date = fecha_rango_hist
            df_hist = df_hist[(df_hist["Fecha"] >= pd.to_datetime(start_date)) & (df_hist["Fecha"] <= pd.to_datetime(end_date))]

        st.subheader("Métricas Principales")
        col1, col2, col3 = st.columns(3)
        col1.metric("PM10 Promedio", f"{df_hist['PM10'].mean():.2f} µg/m³")
        col2.metric("PM10 Máximo", f"{df_hist['PM10'].max():.2f} µg/m³")
        col3.metric("PM10 Mínimo", f"{df_hist['PM10'].min():.2f} µg/m³")

        st.subheader("Evolución de PM10")
        fig_hist = px.line(df_hist, x="Fecha", y="PM10", color="Estacion",
                           title="Evolución de PM10 en el Tiempo")
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("Datos Filtrados")
        st.dataframe(df_hist, use_container_width=True)

# ============================
# PESTAÑA 2: PREDICCIONES
# ============================
with tab2:
    st.subheader("🔮 Generar Predicciones")

    municipios_pred = st.multiselect(
        "Municipio (Predicción):",
        options=sorted(df["Municipio"].dropna().unique()) if df is not None else DEFAULT_MUNICIPIOS,
        default=DEFAULT_MUNICIPIOS if df is None else []
    )
    estaciones_pred = st.multiselect(
        "Estación (Predicción):",
        options=sorted(df["Estacion"].dropna().unique()) if df is not None else DEFAULT_ESTACIONES,
        default=DEFAULT_ESTACIONES if df is None else []
    )
    fecha_rango_pred = st.date_input(
        "Rango de fechas (Predicción):",
        value=[datetime.today(), datetime.today()]
    )

    if st.button("Realizar Predicción"):
        if not municipios_pred or not estaciones_pred:
            st.warning("Por favor selecciona al menos un municipio y una estación.")
        else:
            start_pred, end_pred = fecha_rango_pred if len(fecha_rango_pred) == 2 else (fecha_rango_pred[0], fecha_rango_pred[0])
            fechas_pred = pd.date_range(start=start_pred, end=end_pred)

            inputs_api = []
            for municipio in municipios_pred:
                for estacion in estaciones_pred:
                    for fecha in fechas_pred:
                        inputs_api.append({
                            "Municipio": municipio,
                            "Estacion": estacion,
                            "Año": fecha.year,
                            "Mes": fecha.month,
                            "Dia": fecha.day,
                            "DiaSemana": fecha.day_name()
                        })

            try:
                response = requests.post(API_URL, json={"inputs": inputs_api})
                if response.status_code == 200:
                    results = response.json()
                    df_pred = pd.DataFrame(inputs_api)
                    df_pred["Fecha"] = [
                        datetime(row["Año"], row["Mes"], row["Dia"])
                        for _, row in df_pred.iterrows()
                    ]
                    df_pred["Predicción_PM10"] = results.get("predictions", [None]*len(inputs_api))

                    # Métricas principales de las predicciones
                    st.subheader("📊 Métricas de Predicción")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("PM10 Promedio", f"{df_pred['Predicción_PM10'].mean():.2f} µg/m³")
                    col2.metric("PM10 Máximo", f"{df_pred['Predicción_PM10'].max():.2f} µg/m³")
                    col3.metric("PM10 Mínimo", f"{df_pred['Predicción_PM10'].min():.2f} µg/m³")

                    # Tabla
                    st.subheader("📋 Tabla de Predicciones")
                    st.dataframe(df_pred, use_container_width=True)

                    # Gráfico
                    st.subheader("📈 Gráfico de Predicciones")
                    fig_pred = px.line(
                        df_pred,
                        x="Fecha",
                        y="Predicción_PM10",
                        color="Estacion",
                        markers=True,
                        title="Predicciones de PM10"
                    )
                    st.plotly_chart(fig_pred, use_container_width=True)

                else:
                    st.error(f"Error en API: {response.text}")
            except Exception as e:
                st.error(f"No se pudo conectar con la API: {e}")