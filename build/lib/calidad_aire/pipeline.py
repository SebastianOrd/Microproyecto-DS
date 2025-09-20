from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor
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
    ('model', XGBRegressor(
        reg_alpha=0.1,
        reg_lambda=5.0,
        learning_rate=0.01,
        min_child_weight=5,
        n_estimators=600,
        max_depth=3,
        subsample=0.9,
        colsample_bytree=1.0,
        random_state=13,
        tree_method="hist",
        n_jobs=-1,
        verbosity=0,
    ))
])