import mlflow
import os
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from calidad_aire.processing.data_manager import prepare_datasets
from calidad_aire.config.core import config

from calidad_aire.pipeline import air_quality_pipe

def run_training():
    """
    Orquesta el proceso completo de entrenamiento del modelo.
    """
    load_dotenv()
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI") or getattr(config, "mlflow_tracking_uri", None)
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    exp_name = getattr(config, "mlflow_experiment_name", None)
    if exp_name:
        mlflow.set_experiment(exp_name)
    
    data = prepare_datasets()  # puedes pasar lags/rolls si quieres cambiar
    X_train   = data["X_train"].drop(columns=[data["date_col"]])
    y_train   = data["y_train"]
    X_holdout = data["X_holdout"].drop(columns=[data["date_col"]])
    y_holdout = data["y_holdout"]
    
    with mlflow.start_run(run_name="train_XGB_pipeline") as run:

        print(f"Iniciando corrida de MLflow: {run.info.run_id}")
        
        air_quality_pipe.fit(X_train, y_train)
        
        y_pred = air_quality_pipe.predict(X_holdout)
        
        rmse = float(np.sqrt(mean_squared_error(y_holdout, y_pred)))
        mae = float(mean_absolute_error(y_holdout, y_pred))
        r2 = float(r2_score(y_holdout, y_pred))
        
        print(f"  Holdout RMSE: {rmse:.4f}")
        print(f"  Holdout MAE: {mae:.4f}")
        print(f"  Holdout R2 Score: {r2:.4f}")
        
        xgb_params = {
            k: getattr(config, k)
            for k in [
                "xgb_reg_alpha",
                "xgb_reg_lambda",
                "xgb_learning_rate",
                "xgb_min_child_weight",
                "xgb_n_estimators",
                "xgb_max_depth",
                "xgb_subsample",
                "xgb_colsample_bytree",
                "xgb_tree_method",
            ]
            if hasattr(config, k)
        }
        if xgb_params:
            mlflow.log_params({f"xgb__{k[4:]}": v for k, v in xgb_params.items() if v is not None})
        mlflow.log_params(config.model_dump())
        mlflow.log_metrics({'holdout_rmse': rmse, 'holdout_mae': mae, 'holdout_r2': r2})
        mlflow.sklearn.log_model(
            sk_model=air_quality_pipe,
            artifact_path="model",
            input_example=X_train.head(1),
            #registered_model_name="CalidadAireRisaraldaModel"
        )
        
        print("Modelo registrado en MLflow exitosamente.")

if __name__ == "__main__":
    run_training()