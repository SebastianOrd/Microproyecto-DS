# -*- coding: utf-8 -*-
"""
EDA completo para Calidad del Aire con generación de:
- Tablas descriptivas (por municipio y por estación)
- Histogramas por municipio
- Serie temporal por estación
- Promedio por día de la semana
- Promedio por mes
- Heatmap (Mes × Día de la semana)
- Boxplots por mes y por día de la semana

Nota:
- Solo usa matplotlib (sin seaborn).
- Si existe data/processed/Calidad_del_Aire_enriquecido.csv lo usa; si no, lo crea desde data/raw/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Rutas base
BASE = os.path.dirname(os.path.dirname(__file__))
RAW = os.path.join(BASE, "data", "raw", "Calidad_del_Aire_20250905.csv")
PROCESSED = os.path.join(BASE, "data", "processed", "Calidad_del_Aire_enriquecido.csv")
REPORTS = os.path.join(BASE, "reports")
FIGS = os.path.join(REPORTS, "figures")

os.makedirs(REPORTS, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)
os.makedirs(os.path.dirname(PROCESSED), exist_ok=True)

DIAS_ORDEN = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
DIAS_MAP = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo",
}


def load_data() -> pd.DataFrame:
    """Carga el dataset enriquecido si existe; si no, lo crea desde RAW."""
    if os.path.exists(PROCESSED):
        df = pd.read_csv(PROCESSED)
        # tipado defensivo por si PROCESSED viene de otro run
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df["Medicion"] = pd.to_numeric(df["Medicion"], errors="coerce")
    else:
        df = pd.read_csv(RAW)
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df["Medicion"] = pd.to_numeric(df["Medicion"], errors="coerce")
        # Enriquecimiento temporal
        df["Dia"] = df["Fecha"].dt.day
        df["Mes"] = df["Fecha"].dt.month
        df["Año"] = df["Fecha"].dt.year
        df["DiaSemana"] = df["Fecha"].dt.day_name().map(DIAS_MAP)
        df.to_csv(PROCESSED, index=False)
    # Asegurar columnas clave si vinieron faltantes
    if "Dia" not in df.columns:
        df["Dia"] = df["Fecha"].dt.day
    if "Mes" not in df.columns:
        df["Mes"] = df["Fecha"].dt.month
    if "Año" not in df.columns:
        df["Año"] = df["Fecha"].dt.year
    if "DiaSemana" not in df.columns:
        df["DiaSemana"] = df["Fecha"].dt.day_name().map(DIAS_MAP)
    return df


def save_tables(df: pd.DataFrame) -> None:
    """Guarda estadísticos descriptivos por municipio y por estación."""
    df.groupby("Municipio")["Medicion"].describe().to_csv(
        os.path.join(REPORTS, "resumen_por_municipio.csv")
    )
    df.groupby("Estacion")["Medicion"].describe().to_csv(
        os.path.join(REPORTS, "resumen_por_estacion.csv")
    )


def fig_hist_por_municipio(df: pd.DataFrame) -> None:
    """Histogramas de mediciones por municipio."""
    df.hist(
        column="Medicion",
        by="Municipio",
        bins=30,
        figsize=(12, 8),
        layout=(2, 2),
        sharex=True,
        sharey=True,
    )
    plt.suptitle("Distribución de mediciones por Municipio")
    plt.savefig(os.path.join(FIGS, "hist_medicion_por_municipio.png"), bbox_inches="tight")
    plt.close()


def fig_serie_por_estacion(df: pd.DataFrame) -> None:
    """Serie temporal de mediciones por estación."""
    plt.figure(figsize=(14, 6))
    for estacion in df["Estacion"].dropna().unique():
        subset = df[df["Estacion"] == estacion]
        plt.plot(subset["Fecha"], subset["Medicion"], label=estacion, alpha=0.7)
    plt.title("Evolución temporal de mediciones por estación")
    plt.xlabel("Fecha")
    plt.ylabel("Medición (µg/m³)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "serie_temporal_por_estacion.png"), bbox_inches="tight")
    plt.close()


def fig_promedio_por_dia_semana(df: pd.DataFrame) -> None:
    """Barras con promedio de mediciones por día de la semana (ordenado lun-dom)."""
    plt.figure(figsize=(8, 5))
    (df.groupby("DiaSemana")["Medicion"].mean().reindex(DIAS_ORDEN)).plot(kind="bar")
    plt.title("Promedio de mediciones por día de la semana")
    plt.ylabel("Medición promedio (µg/m³)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "promedio_por_dia_semana.png"), bbox_inches="tight")
    plt.close()


def fig_promedio_por_mes(df: pd.DataFrame) -> None:
    """Barras con promedio de mediciones por mes (1..12)."""
    plt.figure(figsize=(8, 5))
    df.groupby("Mes")["Medicion"].mean().sort_index().plot(kind="bar")
    plt.title("Promedio de mediciones por mes")
    plt.ylabel("Medición promedio (µg/m³)")
    plt.xlabel("Mes")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "promedio_por_mes.png"), bbox_inches="tight")
    plt.close()


def fig_heatmap_mes_dia_semana(df: pd.DataFrame) -> None:
    """Heatmap (imshow) con promedio de mediciones por (DíaSemana × Mes)."""
    pivot = df.pivot_table(
        values="Medicion", index="DiaSemana", columns="Mes", aggfunc="mean"
    )
    pivot = pivot.reindex(DIAS_ORDEN)  # filas
    pivot = pivot.reindex(columns=sorted([c for c in pivot.columns if pd.notnull(c)]))
    plt.figure(figsize=(12, 6))
    plt.imshow(pivot.values, aspect="auto")
    plt.title("Promedio mediciones por Día de la semana y Mes")
    plt.ylabel("Día de la semana")
    plt.xlabel("Mes")
    plt.yticks(ticks=np.arange(len(pivot.index)), labels=pivot.index)
    plt.xticks(ticks=np.arange(len(pivot.columns)), labels=pivot.columns)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "heatmap_mes_dia_semana.png"), bbox_inches="tight")
    plt.close()


def fig_boxplot_por_mes(df: pd.DataFrame) -> None:
    """Boxplot de mediciones por mes."""
    plt.figure(figsize=(10, 6))
    df.boxplot(column="Medicion", by="Mes")
    plt.title("Distribución de mediciones por Mes (Boxplot)")
    plt.suptitle("")
    plt.xlabel("Mes")
    plt.ylabel("Medición (µg/m³)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "boxplot_por_mes.png"), bbox_inches="tight")
    plt.close()


def fig_boxplot_por_dia_semana(df: pd.DataFrame) -> None:
    """Boxplot de mediciones por día de la semana (orden lun-dom)."""
    df = df.copy()
    df["DiaSemana"] = pd.Categorical(df["DiaSemana"], categories=DIAS_ORDEN, ordered=True)
    plt.figure(figsize=(10, 6))
    df.boxplot(column="Medicion", by="DiaSemana")
    plt.title("Distribución de mediciones por Día de la Semana (Boxplot)")
    plt.suptitle("")
    plt.xlabel("Día de la semana")
    plt.ylabel("Medición (µg/m³)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "boxplot_por_dia_semana.png"), bbox_inches="tight")
    plt.close()


def main():
    df = load_data()
    save_tables(df)
    fig_hist_por_municipio(df)
    fig_serie_por_estacion(df)
    fig_promedio_por_dia_semana(df)
    fig_promedio_por_mes(df)
    fig_heatmap_mes_dia_semana(df)
    fig_boxplot_por_mes(df)
    fig_boxplot_por_dia_semana(df)


if __name__ == "__main__":
    main()