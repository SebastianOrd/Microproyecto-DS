# Archivo: src/calidad_aire/pipeline.py

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

from calidad_aire.config.core import config

def create_pipeline(model_name: str) -> Pipeline:
    """Crea el pipeline de Scikit-Learn con el modelo especificado."""

    models = {
        "RandomForest": RandomForestRegressor(
            n_estimators=config.n_estimators,
            max_depth=config.max_depth,
            random_state=config.random_state,
            n_jobs=-1
        ),
        "XGBoost": XGBRegressor(
            n_estimators=config.n_estimators,
            max_depth=config.max_depth,
            random_state=config.random_state,
            n_jobs=-1
        ),
        "LightGBM": LGBMRegressor(
            n_estimators=config.n_estimators,
            max_depth=config.max_depth,
            random_state=config.random_state,
            n_jobs=-1
        )
    }

    if model_name not in models:
        raise ValueError(f"Modelo '{model_name}' no reconocido. Opciones: {list(models.keys())}")

    preprocessor = ColumnTransformer(
        transformers=[
            ('onehot', 
             OneHotEncoder(handle_unknown='ignore', sparse_output=False), 
             config.categorical_features)
        ],
        remainder='passthrough'
    )

    return Pipeline([
        ('preprocessor', preprocessor),
        ('model', models[model_name])
    ])

air_quality_pipe = create_pipeline(model_name=config.model_name)