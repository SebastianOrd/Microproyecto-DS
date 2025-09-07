import pandas as pd
import numpy as np
from calidad_aire.config.core import DATA_DIR, config

def load_dataset() -> pd.DataFrame:
    """Carga el dataset y crea nuevas características de ingeniería."""
    file_path = DATA_DIR / config.data_file
    df = pd.read_csv(file_path)
    df.dropna(subset=[config.target], inplace=True)

    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

    df['dia_del_anio'] = df['Fecha'].dt.dayofyear
    df['semana_del_anio'] = df['Fecha'].dt.isocalendar().week.astype(int)
    df['es_fin_de_semana'] = (df['Fecha'].dt.weekday >= 5).astype(int)

    df['mes_sin'] = np.sin(2 * np.pi * df['Mes'] / 12)
    df['mes_cos'] = np.cos(2 * np.pi * df['Mes'] / 12)
    df['dia_sin'] = np.sin(2 * np.pi * df['Dia'] / 31)
    df['dia_cos'] = np.cos(2 * np.pi * df['Dia'] / 31)

    return df