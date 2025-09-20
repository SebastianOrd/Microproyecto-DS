from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple, Dict

import numpy as np
import pandas as pd

from calidad_aire.config.core import DATA_DIR, config


# =========================
# Defaults (lee de config si existen)
# =========================
DATE_COL: str = getattr(config, "date_col", "Fecha")
TARGET_COL: str = getattr(config, "target", "Medicion")
CAT_GROUP: List[str] = getattr(
    config, "cat_group", ["Municipio", "Estacion", "Diametro aerodinamico"]
)
CAT_COLS: List[str] = getattr(
    config,
    "categorical_features",
    ["Municipio", "Estacion", "Diametro aerodinamico", "DiaSemana"],
)
NUM_COLS: List[str] = getattr(config, "numeric_features", ["Dia", "Mes", "Año"])


# =========================
# 1) Carga y limpieza base
# =========================

def load_dataset() -> pd.DataFrame:
    """Carga el dataset desde DATA_DIR/config y realiza limpieza base mínima.

    - Verifica existencia del archivo
    - Parseo robusto de fecha y orden cronológico
    - Target a numérico y drop de NaN
    """
    file_path: Path = DATA_DIR / config.data_file
    if not file_path.exists():
        raise FileNotFoundError(
            f"No existe el CSV en {file_path}. Ajusta DATA_DIR o config.data_file."
        )

    df = pd.read_csv(file_path)

    # Fecha
    if DATE_COL not in df.columns:
        raise ValueError(
            f"Columna de fecha '{DATE_COL}' no encontrada. Columnas: {list(df.columns)}"
        )
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    if df[DATE_COL].isna().all():
        raise ValueError(f"No se pudo parsear '{DATE_COL}' a datetime.")
    df = df.sort_values(DATE_COL).reset_index(drop=True)

    # Target numérico + drop NaN
    if TARGET_COL not in df.columns:
        raise ValueError(
            f"Target '{TARGET_COL}' no encontrado. Columnas: {list(df.columns)}"
        )
    df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors="coerce")
    missing_y0 = int(df[TARGET_COL].isna().sum())
    if missing_y0:
        print(f"[WARN] Filas con {TARGET_COL} NaN antes de featurización: {missing_y0}")
    df = df.dropna(subset=[TARGET_COL]).reset_index(drop=True)

    return df


# =========================
# 2) Ingeniería temporal por grupo (evita fuga)
# =========================

def add_group_time_features(
    df: pd.DataFrame, lags: Optional[List[int]] = None, rolls: Optional[List[int]] = None
) -> pd.DataFrame:
    """Crea lags y medias móviles del TARGET_COL agrupando por CAT_GROUP.

    Se usa shift(1) en rollings para no mirar el presente.
    """
    if lags is None:
        lags = [1, 7, 30]
    if rolls is None:
        rolls = [7, 30]

    # Validación de columnas
    for col in CAT_GROUP + [TARGET_COL, DATE_COL]:
        if col not in df.columns:
            raise ValueError(f"Falta columna requerida '{col}' para ingeniería temporal.")

    # Lags del target por grupo
    for lag in lags:
        df[f"lag_{lag}"] = df.groupby(CAT_GROUP, dropna=False)[TARGET_COL].shift(lag)

    # Rolling mean con shift(1)
    for w in rolls:
        df[f"rollmean_{w}"] = (
            df.groupby(CAT_GROUP, dropna=False)[TARGET_COL]
            .apply(lambda s: s.shift(1).rolling(w, min_periods=max(3, w // 3)).mean())
            .reset_index(level=CAT_GROUP, drop=True)
        )

    # Reporte y limpieza de NaN introducidos por lags/rollings
    cols_req = [TARGET_COL] + [f"lag_{l}" for l in lags] + [f"rollmean_{w}" for w in rolls]
    missing_after = df[cols_req].isna().sum().to_dict()
    if any(v > 0 for v in missing_after.values()):
        print("[WARN] NaN tras lags/rollings por columnas:", missing_after)

    df = df.dropna(subset=cols_req).reset_index(drop=True)
    return df


# =========================
# 3) Split OUT-OF-TIME por fecha global
# =========================

def temporal_train_holdout_split(
    df: pd.DataFrame,
    holdout_days_if_long: int = 365,
    holdout_frac_if_short: float = 0.2,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    """Split temporal robusto.

    - Si el rango temporal >= ~2 años: usa últimos `holdout_days_if_long` días como holdout.
    - Si no, usa el último `holdout_frac_if_short` del dataset.
    """
    range_days = (df[DATE_COL].max() - df[DATE_COL].min()).days
    if range_days >= 365 * 2:
        cutoff = df[DATE_COL].max() - pd.Timedelta(days=holdout_days_if_long)
    else:
        cutoff = df[DATE_COL].quantile(1.0 - holdout_frac_if_short)

    train_df = df[df[DATE_COL] < cutoff].copy()
    holdout_df = df[df[DATE_COL] >= cutoff].copy()
    if train_df.empty or holdout_df.empty:
        raise ValueError(
            f"Split vacío. Ajusta cutoff. (cutoff={cutoff}, train={len(train_df)}, holdout={len(holdout_df)})"
        )
    return train_df, holdout_df, cutoff


# =========================
# 4) Construcción de matrices X/y
# =========================

def build_feature_matrices(
    train_df: pd.DataFrame,
    holdout_df: pd.DataFrame,
    lags: Optional[List[int]] = None,
    rolls: Optional[List[int]] = None,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, List[str], List[str]]:
    if lags is None:
        lags = [1, 7, 30]
    if rolls is None:
        rolls = [7, 30]

    feature_cols_num = NUM_COLS + [f"lag_{l}" for l in lags] + [f"rollmean_{w}" for w in rolls]
    feature_cols_cat = CAT_COLS

    missing_cols = [
        c
        for c in feature_cols_cat + feature_cols_num + [TARGET_COL, DATE_COL]
        if c not in train_df.columns
    ]
    if missing_cols:
        raise ValueError(f"Faltan columnas tras featurización: {missing_cols}")

    all_feature_cols = feature_cols_num + feature_cols_cat + [DATE_COL]

    X_train = train_df[all_feature_cols].copy()
    y_train = train_df[TARGET_COL].copy()
    X_holdout = holdout_df[all_feature_cols].copy()
    y_holdout = holdout_df[TARGET_COL].copy()

    if y_train.isna().any() or y_holdout.isna().any():
        raise ValueError(
            f"Persisten NaN en y: train={y_train.isna().sum()}, holdout={y_holdout.isna().sum()}."
        )

    return X_train, y_train, X_holdout, y_holdout, feature_cols_num, feature_cols_cat


# =========================
# 5) Orquestador end-to-end
# =========================

def prepare_datasets(lags: Optional[List[int]] = None, rolls: Optional[List[int]] = None) -> Dict[str, object]:
    """Pipeline completo de preparación de datos para entrenamiento/evaluación.

    Devuelve un diccionario con: df, train_df, holdout_df, cutoff, X_train, y_train,
    X_holdout, y_holdout, feature_cols_num, feature_cols_cat, DATE_COL, TARGET_COL.
    """
    df = load_dataset()
    df = add_group_time_features(df, lags=lags, rolls=rolls)
    train_df, holdout_df, cutoff = temporal_train_holdout_split(df)
    (
        X_train,
        y_train,
        X_holdout,
        y_holdout,
        feature_cols_num,
        feature_cols_cat,
    ) = build_feature_matrices(train_df, holdout_df, lags=lags, rolls=rolls)

    return {
        "df": df,
        "train_df": train_df,
        "holdout_df": holdout_df,
        "cutoff": cutoff,
        "X_train": X_train,
        "y_train": y_train,
        "X_holdout": X_holdout,
        "y_holdout": y_holdout,
        "feature_cols_num": feature_cols_num,
        "feature_cols_cat": feature_cols_cat,
        "date_col": DATE_COL,
        "target_col": TARGET_COL,
    }