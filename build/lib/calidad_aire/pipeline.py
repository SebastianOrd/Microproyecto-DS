from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from calidad_aire.config.core import config

air_quality_pipe = Pipeline([
    ('preprocessor', ColumnTransformer(
        transformers=[
            ('onehot', 
             OneHotEncoder(handle_unknown='ignore', sparse_output=False), 
             config.categorical_features)
        ],
        remainder='passthrough'
    )),
    ('model', RandomForestRegressor(
        n_estimators=config.n_estimators,
        max_depth=config.max_depth,
        random_state=config.random_state,
        n_jobs=-1
    ))
])