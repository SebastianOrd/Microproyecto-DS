from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
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
    ('model', LinearRegression())
])