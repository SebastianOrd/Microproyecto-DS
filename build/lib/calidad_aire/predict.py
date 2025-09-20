import pandas as pd
import mlflow
from dotenv import load_dotenv

from calidad_aire.config.core import config

def make_prediction(*, input_data: pd.DataFrame, run_id: str) -> dict:
    """
    Realiza una predicción usando un modelo entrenado desde MLflow.
    """
    load_dotenv()

    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    
    try:
        logged_model_uri = f"runs:/{run_id}/model"
        loaded_model = mlflow.pyfunc.load_model(logged_model_uri)

        predictions = loaded_model.predict(input_data)

        results = {
            "predictions": predictions.tolist(),
            "run_id": run_id,
            "errors": None
        }

    except Exception as e:
        results = {
            "predictions": None,
            "run_id": run_id,
            "errors": str(e)
        }

    return results