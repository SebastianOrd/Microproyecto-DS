from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet
from sklearn.svm import SVR
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

from calidad_aire.config.core import config

def create_pipeline(model_name: str) -> Pipeline:
    """Crea el pipeline de Scikit-Learn con el modelo y preprocesamiento adecuados."""

    preprocessor = ColumnTransformer(
        transformers=[
            ('onehot', 
             OneHotEncoder(handle_unknown='ignore', sparse_output=False), 
             config.categorical_features)
        ],
        remainder='passthrough'
    )

    models = {
        "RandomForest": RandomForestRegressor(n_estimators=config.n_estimators, max_depth=config.max_depth, random_state=config.random_state, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=config.n_estimators, max_depth=config.max_depth, random_state=config.random_state, n_jobs=-1),
        "LightGBM": LGBMRegressor(n_estimators=config.n_estimators, max_depth=config.max_depth, random_state=config.random_state, n_jobs=-1),
        "ElasticNet": ElasticNet(alpha=config.alpha, l1_ratio=config.l1_ratio, random_state=config.random_state),
        "SVR": SVR(C=config.C, gamma=config.gamma)
    }

    if model_name not in models:
        raise ValueError(f"Modelo '{model_name}' no reconocido. Opciones: {list(models.keys())}")

    models_requiring_scaling = ["ElasticNet", "SVR"]

    pipeline_steps = [('preprocessor', preprocessor)]
    if model_name in models_requiring_scaling:
        pipeline_steps.append(('scaler', StandardScaler()))

    pipeline_steps.append(('model', models[model_name]))

    return Pipeline(pipeline_steps)

air_quality_pipe = create_pipeline(model_name=config.model_name)