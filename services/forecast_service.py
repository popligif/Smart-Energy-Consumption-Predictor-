"""
Forecast Service — Real energy consumption predictions
using new 3-phase sensor dataset (29 days, 14 devices, ~7s interval).

Uses sklearn GradientBoostingRegressor (no extra dependencies needed).

Optimized for ultra-fast execution (pure NumPy/list buffers, no DataFrame overhead).
Single 720-step recursive forecast loop instead of repeating loops.
"""
import os
import numpy as np
import pandas as pd
import streamlit as st
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_BASE = os.path.dirname(os.path.dirname(__file__))
NEW_DATASET_PATH = os.path.join(_BASE, "new dataset.csv")


# ── Step 1: Load & preprocess raw sensor data into hourly kW ─────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_hourly_campus_kw(path: str = NEW_DATASET_PATH) -> pd.DataFrame:
    """
    Reads raw 3-phase sensor CSV, computes kW per row, resamples to
    hourly campus-wide total kW.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"New dataset not found: {path}")

    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Apparent power: P ≈ sum(V_i × I_i) / 1000  (kW)
    df["total_kw"] = (
        df["phase1_voltage"] * df["phase1_current"]
        + df["phase2_voltage"] * df["phase2_current"]
        + df["phase3_voltage"] * df["phase3_current"]
    ) / 1000.0

    # Hourly campus total
    df["hour_bucket"] = df["timestamp"].dt.floor("h")
    hourly = (
        df.groupby("hour_bucket")["total_kw"]
        .sum()
        .reset_index()
        .rename(columns={"hour_bucket": "ds", "total_kw": "y"})
        .sort_values("ds")
    )

    # Remove extreme outliers (> 3σ)
    mu, sigma = hourly["y"].mean(), hourly["y"].std()
    hourly = hourly[
        (hourly["y"] >= mu - 3 * sigma) & (hourly["y"] <= mu + 3 * sigma)
    ]
    hourly = hourly.set_index("ds")

    logger.info(f"Loaded {len(hourly)} hourly records from real dataset")
    return hourly


# ── Step 2: Feature engineering ───────────────────────────────────────────────
FEATURE_COLS = [
    "hour", "dow", "is_weekend",
    "hour_sin", "hour_cos", "dow_sin", "dow_cos",
    "lag_1h", "lag_2h", "lag_3h",
    "lag_24h", "lag_48h", "lag_168h",
    "rolling_mean_6h", "rolling_mean_24h", "rolling_std_6h",
]


def _build_features(hourly: pd.DataFrame) -> pd.DataFrame:
    """Adds time + lag features to hourly kW series."""
    df = hourly.copy()
    df["hour"]       = df.index.hour
    df["dow"]        = df.index.dayofweek
    df["is_weekend"] = (df["dow"] >= 5).astype(int)

    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"]  = np.sin(2 * np.pi * df["dow"] / 7)
    df["dow_cos"]  = np.cos(2 * np.pi * df["dow"] / 7)

    df["lag_1h"]           = df["y"].shift(1)
    df["lag_2h"]           = df["y"].shift(2)
    df["lag_3h"]           = df["y"].shift(3)
    df["lag_24h"]          = df["y"].shift(24)
    df["lag_48h"]          = df["y"].shift(48)
    df["lag_168h"]         = df["y"].shift(168)
    df["rolling_mean_6h"]  = df["y"].shift(1).rolling(6, min_periods=1).mean()
    df["rolling_mean_24h"] = df["y"].shift(1).rolling(24, min_periods=1).mean()
    df["rolling_std_6h"]   = df["y"].shift(1).rolling(6, min_periods=1).std().fillna(0)

    return df.dropna()


# ── Step 3: Train model ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_trained_models(path: str = NEW_DATASET_PATH):
    """
    Trains sklearn GradientBoostingRegressor.
    Returns { model, mae, mape, hourly, features }.
    """
    from sklearn.ensemble import GradientBoostingRegressor

    hourly = load_hourly_campus_kw(path)
    feats  = _build_features(hourly)

    X = feats[FEATURE_COLS]
    y = feats["y"]

    # Chronological 75/25 split
    split = int(len(X) * 0.75)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = GradientBoostingRegressor(
        n_estimators=250,
        learning_rate=0.06,
        max_depth=5,
        min_samples_leaf=5,
        subsample=0.85,
        random_state=42,
    )
    model.fit(X_train.values, y_train.values)

    preds  = model.predict(X_test.values)
    errors = np.abs(preds - y_test.values)
    mae    = float(np.mean(errors))
    mape   = float(np.mean(errors / (np.abs(y_test.values) + 1e-6)) * 100)

    logger.info(f"Forecast model trained — MAE={mae:.2f} kW, MAPE={mape:.1f}%")
    return {
        "model": model,
        "mae": mae,
        "mape": mape,
        "hourly": hourly,
        "features": feats,
    }


# ── Step 4: Optimized forecast generator (single-pass recursive loop) ─────────
@st.cache_data(ttl=300, show_spinner=False)
def generate_all_forecasts() -> dict:
    """
    Runs a single 720-step (30-day) recursive forecast loop using fast
    list buffers. Returns a dict containing the generated predictions
    for all four horizons (hour, 24h, 7d, 30d).
    """
    res   = get_trained_models()
    model = res["model"]
    feats = res["features"]
    mae   = res["mae"]

    # Extract indices of lag features to align from our rolling list
    last_ts = feats.index[-1]
    
    hourly = res["hourly"]
    y_seed = list(hourly["y"].values[-168:])
    
    # Pre-calculate time lists for speed
    future_timestamps = [last_ts + timedelta(hours=i) for i in range(1, 721)]
    
    predictions = []
    
    # Quick numpy-friendly rolling standard deviation helper
    def fast_std(vals):
        return float(np.std(vals))

    for i, ts in enumerate(future_timestamps):
        h   = ts.hour
        dow = ts.weekday()
        is_weekend = int(dow >= 5)
        
        h_sin = np.sin(2 * np.pi * h / 24)
        h_cos = np.cos(2 * np.pi * h / 24)
        d_sin = np.sin(2 * np.pi * dow / 7)
        d_cos = np.cos(2 * np.pi * dow / 7)
        
        # Get lags from rolling buffer
        lag_1 = y_seed[-1]
        lag_2 = y_seed[-2]
        lag_3 = y_seed[-3]
        lag_24 = y_seed[-24]
        lag_48 = y_seed[-48]
        lag_168 = y_seed[-168]
        
        # Get rolling mean / std
        roll_6_mean = sum(y_seed[-6:]) / 6.0
        roll_24_mean = sum(y_seed[-24:]) / 24.0
        roll_6_std = fast_std(y_seed[-6:])
        
        # Construct feature vector
        feats_vec = [
            h, dow, is_weekend, h_sin, h_cos, d_sin, d_cos,
            lag_1, lag_2, lag_3, lag_24, lag_48, lag_168,
            roll_6_mean, roll_24_mean, roll_6_std
        ]
        
        # Fast prediction
        pred = max(0.0, float(model.predict([feats_vec])[0]))
        predictions.append(pred)
        
        # Append to rolling buffer
        y_seed.append(pred)
        
        # Keep buffer size compact (168 seeds + future predictions)
        if len(y_seed) > 1000:
            y_seed.pop(0)

    # ── Horizon 1: Next Hour ──
    next_hour_pred = predictions[0]
    next_hour_ts = future_timestamps[0]
    next_hour_dict = {
        "timestamp":    next_hour_ts,
        "predicted_kw": round(next_hour_pred, 1),
        "lower_kw":     round(max(0, next_hour_pred - 1.5 * mae), 1),
        "upper_kw":     round(next_hour_pred + 1.5 * mae, 1),
        "mae":          round(mae, 1),
        "mape":         round(res["mape"], 1),
    }

    # ── Horizon 2: Next 24 Hours ──
    next_24h_records = []
    for idx in range(24):
        p = predictions[idx]
        next_24h_records.append({
            "timestamp":    future_timestamps[idx],
            "predicted_kw": round(p, 1),
            "lower_kw":     round(max(0, p - 1.5 * mae), 1),
            "upper_kw":     round(p + 1.5 * mae, 1),
        })
    next_24h_df = pd.DataFrame(next_24h_records)

    # ── Horizon 3 & 4: 7 Days & 30 Days ──
    all_df = pd.DataFrame({
        "timestamp":    future_timestamps,
        "predicted_kw": predictions
    })
    all_df["date"] = all_df["timestamp"].dt.date
    
    # Group by date for daily kWh sum
    daily_totals = all_df.groupby("date")["predicted_kw"].sum().reset_index()
    daily_totals = daily_totals.rename(columns={"predicted_kw": "daily_kwh"})
    daily_totals["lower_kwh"] = (daily_totals["daily_kwh"] - 24 * mae).clip(lower=0)
    daily_totals["upper_kwh"] = daily_totals["daily_kwh"] + 24 * mae

    # Extract 7 days (including today/first 7 days of predictions)
    next_7d_df = daily_totals.head(7).copy()
    next_30d_df = daily_totals.copy()

    return {
        "next_hour": next_hour_dict,
        "next_24h":  next_24h_df,
        "next_7d":   next_7d_df,
        "next_30d":  next_30d_df
    }


# ── Step 5: Interface wrappers ────────────────────────────────────────────────
def predict_next_hour() -> dict:
    return generate_all_forecasts()["next_hour"]

def predict_next_24h() -> pd.DataFrame:
    return generate_all_forecasts()["next_24h"]

def predict_next_7days() -> pd.DataFrame:
    return generate_all_forecasts()["next_7d"]

def predict_next_30days() -> pd.DataFrame:
    return generate_all_forecasts()["next_30d"]

def get_model_metrics() -> dict:
    res = get_trained_models()
    return {"mae": res["mae"], "mape": res["mape"]}

def get_historical_hourly() -> pd.DataFrame:
    return load_hourly_campus_kw()
