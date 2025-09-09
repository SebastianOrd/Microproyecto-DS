import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

mlflow.set_tracking_uri("http://52.23.182.67:5000")

df = pd.read_csv('data/processed/Calidad_del_Aire_enriquecido.csv')

df = df.dropna(subset=['Medicion']) 
X = df[['Municipio', 'Estacion', 'Año', 'Mes', 'Dia', 'DiaSemana']]
y = df['Medicion']

split_index = int(len(df) * 0.8)
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

mlflow.set_experiment("Proyeccion_Calidad_Aire_Risaralda")

with mlflow.start_run():
    n_estimators = 150
    max_depth = 15

    mlflow.log_param("modelo", "RandomForestRegressor")
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("features", X.columns.to_list())

    preprocessor = make_column_transformer(
        (OneHotEncoder(handle_unknown='ignore'), ['Municipio', 'Estacion', 'DiaSemana']),
        remainder='passthrough'
    )
    
    model = make_pipeline(preprocessor, RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=-1))
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"RMSE: {rmse}")
    print(f"MAE: {mae}")
    print(f"R2 Score: {r2}")
    
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("r2", r2)
    
    mlflow.sklearn.log_model(model, "random_forest_model")

print("Entrenamiento completado y registrado en el servidor remoto de MLflow.")9