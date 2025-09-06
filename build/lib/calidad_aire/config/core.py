from pathlib import Path
from typing import List
import yaml
from pydantic import BaseModel

CONFIG_FILE_PATH = Path(__file__).parent.parent / "config.yml"
ROOT_DIR = CONFIG_FILE_PATH.parent.parent.parent.parent
DATA_DIR = ROOT_DIR / 'data' / 'processed'

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
    
    with open(cfg_path, 'r') as conf_file:
        return yaml.safe_load(conf_file)

def create_and_validate_config(parsed_config: dict = None) -> AppConfig:
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()
    return AppConfig(**parsed_config)

config = create_and_validate_config()