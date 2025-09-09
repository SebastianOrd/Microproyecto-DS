from pathlib import Path
from typing import List
import yaml
from pydantic import BaseModel

ROOT_DIR = Path.cwd() 

CONFIG_DIR = ROOT_DIR / 'src' / 'calidad_aire'
DATA_DIR = ROOT_DIR / 'data' / 'processed'
CONFIG_FILE_PATH = CONFIG_DIR / 'config.yml'

class AppConfig(BaseModel):
    data_file: str
    target: str
    features: List[str]
    categorical_features: List[str]
    test_size: float
    random_state: int
    n_estimators: int
    max_depth: int
    mlflow_experiment_name: str
    mlflow_tracking_uri: str

def find_config_file() -> Path:
    if CONFIG_FILE_PATH.is_file():
        return CONFIG_FILE_PATH
    raise FileNotFoundError(f"El archivo de configuración no se encontró en: {CONFIG_FILE_PATH}")

def fetch_config_from_yaml(cfg_path: Path = None) -> dict:
    if not cfg_path:
        cfg_path = find_config_file()

    with open(cfg_path, 'r', encoding="utf-8") as conf_file:
        return yaml.safe_load(conf_file)

def create_and_validate_config(parsed_config: dict = None) -> AppConfig:
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()
    return AppConfig(**parsed_config)

config = create_and_validate_config()