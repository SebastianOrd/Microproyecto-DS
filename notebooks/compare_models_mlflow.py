# gridsearch_ts_mlflow_calidad_aire.py

import os
from pathlib import Path
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
import xgboost

from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures, FunctionTransformer, QuantileTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import make_scorer, r2_score, mean_absolute_error
os.environ["MLFLOW_TRACKING_URI"] = "http://52.23.182.67:5000"
os.environ["MLFLOW_TRACKING_USERNAME"] = "mlflow_user"
os.environ["MLFLOW_TRACKING_PASSWORD"] = "p4ssw0rd_1234"
EXPERIMENT_NAME = "Proyeccion_Calidad_Aire_Risaralda_XGB2"

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
mlflow.set_experiment(EXPERIMENT_NAME)
# >=1.4 (1.6+ eliminó 'squared'): usar root_mean_squared_error si existe
try:
    from sklearn.metrics import root_mean_squared_error
    RMSE_SCORER = make_scorer(root_mean_squared_error, greater_is_better=False)
    def rmse(y_true, y_pred): return root_mean_squared_error(y_true, y_pred)
except Exception:
    from sklearn.metrics import mean_squared_error
    RMSE_SCORER = make_scorer(lambda yt, yp: mean_squared_error(yt, yp) ** 0.5, greater_is_better=False)
    def rmse(y_true, y_pred): return mean_squared_error(y_true, y_pred) ** 0.5

# Modelos base
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.svm import SVR

# XGBoost opcional
try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except Exception:
    HAS_XGB = False

HAS_ELASTIC = False
# =================== CONFIGURACIÓN DE TUS COLUMNAS ===================
# En local:
CSV_PATH = Path("data/processed/Calidad_del_Aire_enriquecido.csv")
# En Docker, usa:
# CSV_PATH = Path("/app/data/processed/Calidad_del_Aire_enriquecido.csv")

DATE_COL   = "Fecha"
TARGET_COL = "Medicion"

# Categóricas reales y grupo para lags/rollings sin fuga entre series
CAT_GROUP = ["Municipio", "Estacion", "Diametro aerodinamico"]
CAT_COLS  = ["Municipio", "Estacion", "Diametro aerodinamico", "DiaSemana"]

# Numéricas reales
NUM_COLS  = ["Dia", "Mes", "Año"]  # luego añadimos lags/rollings

N_SPLITS = 5   # nº de folds temporales (TimeSeriesSplit)
# =====================================================================


# ============ 1) Carga y orden cronológico ============
if not CSV_PATH.exists():
    raise FileNotFoundError(f"No existe el CSV en {CSV_PATH}. Ajusta la ruta.")

df = pd.read_csv(CSV_PATH)

# Parseo robusto de fecha y orden
df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
if df[DATE_COL].isna().all():
    raise ValueError(f"No se pudo parsear '{DATE_COL}' a datetime.")
df = df.sort_values(DATE_COL).reset_index(drop=True)

if TARGET_COL not in df.columns:
    raise ValueError(f"Target '{TARGET_COL}' no encontrado. Columnas: {list(df.columns)}")

# ============ 2) Limpieza del target (sin NaN) ============
# Forzar a numérico y eliminar filas sin target ANTES de featurizar
df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors="coerce")
missing_y0 = df[TARGET_COL].isna().sum()
if missing_y0:
    print(f"[WARN] Filas con {TARGET_COL} NaN antes de featurización: {missing_y0}")
df = df.dropna(subset=[TARGET_COL]).reset_index(drop=True)

# ============ 3) Ingeniería temporal por grupo (evita fuga) ============
# Lags del target por grupo
lags = [1, 7, 30]
for lag in lags:
    df[f"lag_{lag}"] = (
        df.groupby(CAT_GROUP, dropna=False)[TARGET_COL].shift(lag)
    )

# Rolling means con shift(1) para no mirar el presente
rolls = [7, 30]
for w in rolls:
    df[f"rollmean_{w}"] = (
        df.groupby(CAT_GROUP, dropna=False)[TARGET_COL]
          .apply(lambda s: s.shift(1).rolling(w, min_periods=max(3, w//3)).mean())
          .reset_index(level=CAT_GROUP, drop=True)
    )

# Elimina NaN generados por lags/rollings (y re-checa target por seguridad)
cols_req = [TARGET_COL] + [f"lag_{l}" for l in lags] + [f"rollmean_{w}" for w in rolls]
missing_after = df[cols_req].isna().sum().to_dict()
if any(v > 0 for v in missing_after.values()):
    print("[WARN] NaN tras lags/rollings por columnas:", missing_after)
df = df.dropna(subset=cols_req).reset_index(drop=True)

# ============ 4) Split por fecha: train vs holdout OUT-OF-TIME ============
range_days = (df[DATE_COL].max() - df[DATE_COL].min()).days
if range_days >= 365 * 2:
    cutoff = df[DATE_COL].max() - pd.Timedelta(days=365)  # últimos ~12 meses como holdout
else:
    cutoff = df[DATE_COL].quantile(0.8)  # 20% final cronológico si hay menos datos

train_df   = df[df[DATE_COL] <  cutoff].copy()
holdout_df = df[df[DATE_COL] >= cutoff].copy()
if train_df.empty or holdout_df.empty:
    raise ValueError(f"Split vacío. Ajusta cutoff. (cutoff={cutoff}, train={len(train_df)}, holdout={len(holdout_df)})")

# Matrices
feature_cols_num = NUM_COLS + [f"lag_{l}" for l in lags] + [f"rollmean_{w}" for w in rolls]
feature_cols_cat = CAT_COLS
all_feature_cols = feature_cols_num + feature_cols_cat + [DATE_COL]

missing_cols = [c for c in feature_cols_cat + feature_cols_num + [TARGET_COL, DATE_COL] if c not in df.columns]
if missing_cols:
    raise ValueError(f"Faltan columnas en el CSV: {missing_cols}")

X_train   = train_df[all_feature_cols].copy()
y_train   = train_df[TARGET_COL].copy()
X_holdout = holdout_df[all_feature_cols].copy()
y_holdout = holdout_df[TARGET_COL].copy()

# Verificación final de NaN en y
if y_train.isna().any() or y_holdout.isna().any():
    raise ValueError(
        f"Persisten NaN en y: train={y_train.isna().sum()}, holdout={y_holdout.isna().sum()}."
    )

# ============ 5) Preprocesamiento compartido ============
numeric_pipe = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
categorical_pipe = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("ohe", OneHotEncoder(handle_unknown="ignore"))
])

preprocess = ColumnTransformer(
    transformers=[
        ("num", numeric_pipe, feature_cols_num),
        ("cat", categorical_pipe, feature_cols_cat),
    ],
    remainder="drop"
)

# ============ 6) Pipelines por modelo ============
if HAS_ELASTIC:
    pipelines = {
        "ElasticNet":   Pipeline([("preprocess", preprocess), ("model", ElasticNet(random_state=13))]),
    }
if HAS_XGB:
    pipelines = {}
    pipelines["XGBRegressor"] = Pipeline([
        ("preprocess", preprocess),
        ("model", XGBRegressor(
            random_state=13, tree_method="hist", n_estimators=400, verbosity=0
        ))
    ])

# ============ 7) Grids de hiperparámetros ============
if not HAS_ELASTIC:
    param_grids = {
        "ElasticNet": {
            "model__alpha": [0.01, 0.1, 1.0],
            "model__l1_ratio": [0.2, 0.5, 0.8],
            "model__fit_intercept": [True, False],
            "model__selection": ["cyclic", "random"]
        }
    }
if HAS_XGB:
    param_grids["XGBRegressor"] = {
    "model__n_estimators": [600, 1000],      # más árboles + lr más bajo
    "model__learning_rate": [0.05, 0.03, 0.01],
    "model__max_depth": [3, 5, 7],
    "model__min_child_weight": [3, 5],
    "model__subsample": [0.9, 1.0],
    "model__colsample_bytree": [0.9, 1.0],
    "model__reg_alpha": [0.1, 1.0],     # L1
    "model__reg_lambda": [5.0, 10.0],   # L2
}

# ============ 8) CV temporal (TimeSeriesSplit) ============
H_TEST = max(60, int(0.1 * len(X_train)))      # ~10% del train por fold (mín. 60)
tscv = TimeSeriesSplit(n_splits=N_SPLITS, test_size=H_TEST, gap=0)

scoring = {
    "rmse": RMSE_SCORER,                                   # minimizar
    "mae": make_scorer(mean_absolute_error, greater_is_better=False),
    "r2":  make_scorer(r2_score)                           # maximizar
}

# ============ 9) Función para correr Grid + MLflow ============
def run_grid_ts_and_log(model_name, pipe, grid, experiment=EXPERIMENT_NAME):
    mlflow.set_experiment(experiment)

    gs = GridSearchCV(
        estimator=pipe,
        param_grid=grid,
        scoring=scoring,
        refit="rmse",                 # mejor = menor RMSE (más negativo)
        cv=tscv,
        n_jobs=-1,
        verbose=0,
        return_train_score=False,
    )

    with mlflow.start_run(run_name=f"{model_name}__grid_ts"):
        # ¡OJO! excluimos 'Fecha' del fit/predict (no entra al ColumnTransformer)
        gs.fit(X_train.drop(columns=[DATE_COL]), y_train)

        res = gs.cv_results_
        n = len(res["params"])

        # Log de TODOS los candidatos como child runs
        for i in range(n):
            with mlflow.start_run(run_name=f"{model_name}__cand_{i}", nested=True):
                mlflow.log_params(res["params"][i])
                mean_rmse = -res["mean_test_rmse"][i]
                mean_mae  = -res["mean_test_mae"][i]
                mean_r2   =  res["mean_test_r2"][i]
                mlflow.log_metrics({"cv_rmse": mean_rmse, "cv_mae": mean_mae, "cv_r2": mean_r2})
                mlflow.set_tags({
                    "model_family": model_name,
                    "cv": "TimeSeriesSplit",
                    "kind": "grid_candidate"
                })

        # Mejor en CV
        best_idx    = gs.best_index_
        best_params = res["params"][best_idx]
        best_rmse   = -res["mean_test_rmse"][best_idx]
        best_mae    = -res["mean_test_mae"][best_idx]
        best_r2     =  res["mean_test_r2"][best_idx]

        mlflow.log_params({f"best__{k}": v for k, v in best_params.items()})
        mlflow.log_metrics({"best_cv_rmse": best_rmse, "best_cv_mae": best_mae, "best_cv_r2": best_r2})
        mlflow.set_tags({"model_family": model_name, "summary": "best_cv_ts"})

        # Reentrena el mejor con TODO el train cronológico
        best_pipe = gs.best_estimator_
        best_pipe.fit(X_train.drop(columns=[DATE_COL]), y_train)

        # Holdout OUT-OF-TIME
        yph = best_pipe.predict(X_holdout.drop(columns=[DATE_COL]))
        rmse_holdout = rmse(y_holdout, yph)
        mae_holdout  = mean_absolute_error(y_holdout, yph)
        r2_holdout   = r2_score(y_holdout, yph)

        mlflow.log_metrics({
            "holdout_rmse": rmse_holdout,
            "holdout_mae": mae_holdout,
            "holdout_r2":  r2_holdout
        })

        # Log del modelo final listo para servir
        mlflow.sklearn.log_model(
            sk_model=best_pipe,
            artifact_path="model",
        )

        # (Opcional) guarda predicciones de holdout como artefacto
        preds_df = pd.DataFrame({
            DATE_COL: X_holdout[DATE_COL].values,
            "y_true": y_holdout.values,
            "y_pred": yph
        })
        tmp_csv = "holdout_predictions.csv"
        preds_df.to_csv(tmp_csv, index=False)
        mlflow.log_artifact(tmp_csv)

        print(f"[{model_name}] best_cv_rmse={best_rmse:.4f} | holdout_rmse={rmse_holdout:.4f} | holdout_r2={r2_holdout:.4f}")
        return gs

# ============ 10) Ejecuta grids ============
if __name__ == "__main__":
    for name, pipe in pipelines.items():
        grid = param_grids.get(name, {})
        if not grid:
            continue
        run_grid_ts_and_log(name, pipe, grid)