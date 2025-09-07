import mlflow
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from calidad_aire.config.core import config
from calidad_aire.processing.data_manager import load_dataset
from calidad_aire.pipeline import air_quality_pipe

def run_training():
    """
    Orquesta el proceso completo de entrenamiento del modelo.
    """
    load_dotenv()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment(config.mlflow_experiment_name)
    
    data = load_dataset()
    X = data[config.features]
    y = data[config.target]
    
    split_index = int(len(data) * (1 - config.test_size))
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
    
    with mlflow.start_run() as run:

        print(f"Iniciando corrida de MLflow: {run.info.run_id}")
        
        air_quality_pipe.fit(X_train, y_train)
        
        y_pred = air_quality_pipe.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  R2 Score: {r2:.4f}")
        
        mlflow.log_params(config.model_dump())
        mlflow.log_metrics({'rmse': rmse, 'mae': mae, 'r2': r2})
        mlflow.sklearn.log_model(
            sk_model=air_quality_pipe,
            artifact_path="model",
            input_example=X_train.head(1),
            #registered_model_name="CalidadAireRisaraldaModel"
        )
        
        print("Modelo registrado en MLflow exitosamente.")

if __name__ == "__main__":
    run_training()