"""
Service layer for scenario-based ML energy predictions, feature importances, and evaluation metrics (FR-4).
"""
import numpy as np
import pandas as pd
import logging
import streamlit as st
from typing import Dict, Any, Tuple, List, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from services.data_service import DataService

logger = logging.getLogger(__name__)


@st.cache_resource(show_spinner="Training ML models (one-time)...")
def _train_ml_models(csv_path: str) -> Dict[str, Any]:
    """
    Module-level cached function: trains all candidate models once per session.
    Using @st.cache_resource because sklearn Pipelines are not serializable by st.cache_data.
    Returns a dict with best_pipeline, model_metrics, feature_importances, best_model_name.
    """
    from services.data_service import _load_and_process_csv
    df = _load_and_process_csv(csv_path)

    features = [
        "Building", "Hour", "Temperature", "Humidity",
        "Occupancy", "Running Computers", "Running ACs",
        "Lighting Load", "HVAC Load"
    ]
    target = "Energy Consumption"

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    categorical_features = ["Building"]
    numeric_features = [
        "Hour", "Temperature", "Humidity", "Occupancy",
        "Running Computers", "Running ACs", "Lighting Load", "HVAC Load"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ]
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42),
    }

    best_r2 = -float("inf")
    best_model_name = ""
    best_pipeline = None
    model_metrics: Dict[str, Dict[str, float]] = {}

    for name, model in models.items():
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)

        y_test_arr = np.array(y_test)
        y_pred_arr = np.array(y_pred)
        mape = np.mean(np.abs((y_test_arr - y_pred_arr) / np.maximum(1e-5, y_test_arr))) * 100

        r2 = r2_score(y_test, y_pred)

        model_metrics[name] = {
            "MAE": round(mae, 3),
            "RMSE": round(rmse, 3),
            "MAPE (%)": round(mape, 3),
            "R²": round(r2, 4),
        }

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_pipeline = pipeline

    logger.info(f"ML Comparison Complete. Best model: {best_model_name} with R²: {best_r2:.4f}")

    # Feature importances
    feature_names: List[str] = []
    feature_importances: Dict[str, float] = {}

    if best_pipeline:
        prep = best_pipeline.named_steps["preprocessor"]
        regressor = best_pipeline.named_steps["regressor"]

        cat_encoder = prep.named_transformers_["cat"]
        cat_features_encoded = cat_encoder.get_feature_names_out(["Building"]).tolist()
        feature_names = numeric_features + cat_features_encoded

        importances = np.zeros(len(feature_names))
        if hasattr(regressor, "feature_importances_"):
            importances = regressor.feature_importances_
        elif hasattr(regressor, "coef_"):
            importances = np.abs(regressor.coef_)
        else:
            importances = np.ones(len(feature_names)) / len(feature_names)

        total = np.sum(importances)
        if total > 0:
            importances = importances / total

        feature_importances = {n: float(v) for n, v in zip(feature_names, importances)}

    return {
        "best_pipeline": best_pipeline,
        "best_model_name": best_model_name,
        "model_metrics": model_metrics,
        "feature_importances": feature_importances,
        "feature_names": feature_names,
    }


class MLService:
    """Manages training, evaluation, comparison, and prediction pipelines for scenario forecasting."""

    def __init__(self) -> None:
        self.data_service = DataService()
        result = _train_ml_models(self.data_service.csv_path)
        self.best_model_name: str = result["best_model_name"]
        self.best_pipeline: Optional[Pipeline] = result["best_pipeline"]
        self.model_metrics: Dict[str, Dict[str, float]] = result["model_metrics"]
        self.feature_importances: Dict[str, float] = result["feature_importances"]
        self.feature_names: List[str] = result["feature_names"]

    def get_comparison_metrics(self) -> Dict[str, Dict[str, float]]:
        """Returns performance metrics for all compared models."""
        return self.model_metrics

    def predict_scenario(
        self,
        building: str,
        hour: int,
        temp: float,
        humidity: float,
        occupancy: int,
        running_acs: int,
        running_computers: int,
        lighting_load: float,
        hvac_load: float,
    ) -> Dict[str, Any]:
        """Runs interactive scenario prediction and computes deviations from historical averages (FR-4)."""
        if not self.best_pipeline:
            raise ValueError("Model pipeline has not been trained yet.")

        input_data = pd.DataFrame([{
            "Building": building,
            "Hour": hour,
            "Temperature": temp,
            "Humidity": humidity,
            "Occupancy": occupancy,
            "Running Computers": running_computers,
            "Running ACs": running_acs,
            "Lighting Load": lighting_load,
            "HVAC Load": hvac_load,
        }])

        predicted_energy = float(self.best_pipeline.predict(input_data)[0])
        predicted_energy = max(0.1, predicted_energy)

        settings = self.data_service.settings_manager.load_settings()
        tariff = settings.get("electricity_tariff")
        carbon_factor = settings.get("carbon_factor")

        predicted_cost = predicted_energy * tariff
        predicted_carbon = predicted_energy * carbon_factor

        df_hist = self.data_service.load_dataset()
        hist_match = df_hist[(df_hist["Building"] == building) & (df_hist["Hour"] == hour)]

        if not hist_match.empty:
            baseline_energy = float(hist_match["Energy Consumption"].mean())
        else:
            baseline_energy = float(df_hist[df_hist["Building"] == building]["Energy Consumption"].mean())

        diff_energy = predicted_energy - baseline_energy
        pct_change = (diff_energy / baseline_energy) * 100

        drivers = []
        if not hist_match.empty:
            if running_acs > hist_match["Running ACs"].mean():
                drivers.append("above-average Air Conditioner usage")
            if occupancy > hist_match["Occupancy"].mean():
                drivers.append("higher building occupancy")
            if temp > hist_match["Temperature"].mean():
                drivers.append("elevated outdoor temperature")

        driver_text = " and ".join(drivers) if drivers else "typical baseline patterns"

        explanation = (
            f"The predicted energy consumption is **{predicted_energy:.2f} kW**, which is "
            f"**{abs(pct_change):.1f}% {'higher' if diff_energy >= 0 else 'lower'}** than the historical "
            f"baseline of **{baseline_energy:.2f} kW** for {building} at Hour {hour}. "
            f"This deviation is primarily influenced by {driver_text}."
        )

        return {
            "predicted_energy_kw": round(predicted_energy, 2),
            "predicted_cost_inr": round(predicted_cost, 2),
            "predicted_carbon_kg": round(predicted_carbon, 2),
            "baseline_energy_kw": round(baseline_energy, 2),
            "difference_kw": round(diff_energy, 2),
            "percentage_change": round(pct_change, 2),
            "explanation": explanation,
        }
