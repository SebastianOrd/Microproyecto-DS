import json
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from loguru import logger
#from model import __version__ as model_version
from calidad_aire.predict import make_prediction

from app_api  import __version__, schemas
from app_api.config import settings

api_router = APIRouter()

# Ruta para verificar que la API se esté ejecutando correctamente
@api_router.get("/health", response_model=schemas.Health, status_code=200)
def health() -> dict:
    """
    Root Get
    """
    health = schemas.Health(
        #name=settings.PROJECT_NAME, api_version=__version__, model_version=model_version
        name=settings.PROJECT_NAME, api_version=__version__, model_version="0.1.0"
    )

    return health.dict()

# Ruta para realizar las predicciones
@api_router.post("/predict", response_model=schemas.PredictionResults, status_code=200)
async def predict(input_data: schemas.MultipleDataInputs) -> Any:
    """
    Prediccion usando el modelo de contaminacion del aire
    """
    MLFLOW_RUN_ID = "d01a7a84488d4849a048119fa83734a3"
    input_df = pd.DataFrame(jsonable_encoder(input_data.inputs))

    logger.info(f"Making prediction on inputs: {input_data.inputs}")
    results = make_prediction(input_data=input_df.replace({np.nan: None}),run_id=MLFLOW_RUN_ID)
    errors = results.get("errors")
    if errors:
        # Acepta dict/list directo
        if isinstance(errors, (dict, list)):
            raise HTTPException(status_code=400, detail=errors)

        # Si es string, intenta parsear; si falla, devuélvelo como texto
        if isinstance(errors, str):
            s = errors.strip()
            if s.lower() in ("none", "null", ""):
                raise HTTPException(status_code=400, detail="Unknown validation error")
            try:
                raise HTTPException(status_code=400, detail=json.loads(s))
            except Exception:
                raise HTTPException(status_code=400, detail=s)
    
    logger.info(f"Prediction results: {results.get('predictions')}")

    # Si no hay errores, devuelve predicciones
    return {
        "predictions": results.get("predictions"),
        "version": results.get("version"),
    }
