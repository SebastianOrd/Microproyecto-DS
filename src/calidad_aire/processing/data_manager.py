import pandas as pd
from calidad_aire.config.core import DATA_DIR, config

def load_dataset() -> pd.DataFrame:
    """Carga y pre-procesa el dataset."""
    file_path = DATA_DIR / config.data_file
    df = pd.read_csv(file_path)
    df.dropna(subset=[config.target], inplace=True)
    return df