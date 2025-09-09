import pandas as pd
import mlflow
from dotenv import load_dotenv

def make_prediction(*, input_data: pd.DataFrame, run_id: str) -> dict:
    """
    Realiza una predicción usando un modelo entrenado desde MLflow.

    Args:
        input_data: DataFrame con los datos de entrada para la predicción.
                    Debe contener las columnas que el modelo espera.
        run_id: El ID de la corrida (Run ID) de MLflow del modelo que se desea usar.

    Returns:
        Un diccionario con las predicciones, el ID de la corrida y posibles errores.
    """
    load_dotenv()

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