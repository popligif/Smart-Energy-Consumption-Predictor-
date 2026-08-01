"""
Forecast Service — Real energy consumption predictions
using new 3-phase sensor dataset (29 days, 14 devices, ~7s interval).

Uses sklearn GradientBoostingRegressor (no extra dependencies needed).

Horizons:
  - Next 1 hour
  - Next 24 hours (hourly profile)
  - Next 7 days   (daily totals)
  - Next 30 days  (monthly indicative)

Performance: everything cached via st.cache_data / st.cache_resource.
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
    model.fit(X_train, y_train)

    preds  = model.predict(X_test)
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


# ── Step 4: Prediction helpers ────────────────────────────────────────────────
def _make_future_row(last_row, target_dt):
    """Build feature row for a future timestamp."""
    h   = target_dt.hour
    dow = target_dt.weekday()
    return {
        "hour": h, "dow": dow, "is_weekend": int(dow >= 5),
        "hour_sin": np.sin(2 * np.pi * h / 24),
        "hour_cos": np.cos(2 * np.pi * h / 24),
        "dow_sin":  np.sin(2 * np.pi * dow / 7),
        "dow_cos":  np.cos(2 * np.pi * dow / 7),
        "lag_1h":           last_row.get("lag_1h", last_row["y"]),
        "lag_2h":           last_row.get("lag_2h", last_row["y"]),
        "lag_3h":           last_row.get("lag_3h", last_row["y"]),
        "lag_24h":          last_row.get("lag_24h", last_row["y"]),
        "lag_48h":          last_row.get("lag_48h", last_row["y"]),
        "lag_168h":         last_row.get("lag_168h", last_row["y"]),
        "rolling_mean_6h":  last_row.get("rolling_mean_6h", last_row["y"]),
        "rolling_mean_24h": last_row.get("rolling_mean_24h", last_row["y"]),
        "rolling_std_6h":   last_row.get("rolling_std_6h", 0),
    }


@st.cache_data(ttl=300, show_spinner=False)
def predict_next_hour() -> dict:
    """Returns next-hour kW prediction + confidence interval."""
    res   = get_trained_models()
    model = res["model"]
    feats = res["features"]
    mae   = res["mae"]

    last_row = feats.iloc[-1]
    last_ts  = feats.index[-1]
    next_ts  = last_ts + timedelta(hours=1)
    row      = _make_future_row(last_row, next_ts)

    pred = max(0, float(model.predict(pd.DataFrame([row])[FEATURE_COLS])[0]))
    return {
        "timestamp":    next_ts,
        "predicted_kw": round(pred, 1),
        "lower_kw":     round(max(0, pred - 1.5 * mae), 1),
        "upper_kw":     round(pred + 1.5 * mae, 1),
        "mae":          round(mae, 1),
        "mape":         round(res["mape"], 1),
    }


@st.cache_data(ttl=300, show_spinner=False)
def predict_next_24h() -> pd.DataFrame:
    """Returns 24-hour forecast DataFrame."""
    res   = get_trained_models()
    model = res["model"]
    feats = res["features"]
    mae   = res["mae"]

    last_row = feats.iloc[-1].copy()
    last_ts  = feats.index[-1]
    records  = []

    for i in range(1, 25):
        ts   = last_ts + timedelta(hours=i)
        row  = _make_future_row(last_row, ts)
        pred = max(0, float(model.predict(pd.DataFrame([row])[FEATURE_COLS])[0]))
        records.append({
            "timestamp":    ts,
            "predicted_kw": round(pred, 1),
            "lower_kw":     round(max(0, pred - 1.5 * mae), 1),
            "upper_kw":     round(pred + 1.5 * mae, 1),
        })
        last_row = last_row.copy()
        last_row["lag_1h"] = pred

    return pd.DataFrame(records)


@st.cache_data(ttl=1800, show_spinner=False)
def predict_next_7days() -> pd.DataFrame:
    """Returns daily forecast totals for next 7 days."""
    res   = get_trained_models()
    model = res["model"]
    feats = res["features"]
    mae   = res["mae"]

    last_row = feats.iloc[-1].copy()
    last_ts  = feats.index[-1]
    records  = []

    for i in range(1, 169):
        ts   = last_ts + timedelta(hours=i)
        row  = _make_future_row(last_row, ts)
        pred = max(0, float(model.predict(pd.DataFrame([row])[FEATURE_COLS])[0]))
        records.append({"timestamp": ts, "predicted_kw": pred})
        last_row = last_row.copy()
        last_row["lag_1h"] = pred

    df = pd.DataFrame(records)
    df["date"] = df["timestamp"].dt.date
    daily = df.groupby("date")["predicted_kw"].sum().reset_index()
    daily = daily.rename(columns={"predicted_kw": "daily_kwh"})
    daily["lower_kwh"] = (daily["daily_kwh"] - 24 * mae).clip(lower=0)
    daily["upper_kwh"] = daily["daily_kwh"] + 24 * mae
    return daily


@st.cache_data(ttl=3600, show_spinner=False)
def predict_next_30days() -> pd.DataFrame:
    """Returns indicative monthly forecast — daily totals for 30 days."""
    res   = get_trained_models()
    model = res["model"]
    feats = res["features"]
    mae   = res["mae"]

    last_row = feats.iloc[-1].copy()
    last_ts  = feats.index[-1]
    records  = []

    for i in range(1, 721):
        ts   = last_ts + timedelta(hours=i)
        row  = _make_future_row(last_row, ts)
        pred = max(0, float(model.predict(pd.DataFrame([row])[FEATURE_COLS])[0]))
        records.append({"timestamp": ts, "predicted_kw": pred})
        last_row = last_row.copy()
        last_row["lag_1h"] = pred

    df = pd.DataFrame(records)
    df["date"] = df["timestamp"].dt.date
    daily = df.groupby("date")["predicted_kw"].sum().reset_index()
    daily = daily.rename(columns={"predicted_kw": "daily_kwh"})
    daily["lower_kwh"] = (daily["daily_kwh"] - 24 * mae).clip(lower=0)
    daily["upper_kwh"] = daily["daily_kwh"] + 24 * mae
    return daily


def get_model_metrics() -> dict:
    """Returns MAE and MAPE of the trained model."""
    res = get_trained_models()
    return {"mae": res["mae"], "mape": res["mape"]}


def get_historical_hourly() -> pd.DataFrame:
    """Returns the processed hourly campus kW series for overlays."""
    return load_hourly_campus_kw()
