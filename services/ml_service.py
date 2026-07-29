"""
Service layer for scenario-based ML energy predictions, feature importances, and evaluation metrics (FR-4).
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Tuple, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from services.data_service import DataService

logger = logging.getLogger(__name__)

class MLService:
    """Manages training, evaluation, comparison, and prediction pipelines for scenario forecasting."""
    
    def __init__(self) -> None:
        self.data_service = DataService()
        self.best_model_name: str = ""
        self.best_pipeline: Optional[Pipeline] = None
        self.model_metrics: Dict[str, Dict[str, float]] = {}
        self.feature_names: List[str] = []
        self.feature_importances: Dict[str, float] = {}
        self._train_and_evaluate_all()

    def _train_and_evaluate_all(self) -> None:
        """Trains and compares regression models, selecting the best configuration."""
        df = self.data_service.load_dataset()
        
        # Define features and target
        features = [
            "Building", "Hour", "Temperature", "Humidity", 
            "Occupancy", "Running Computers", "Running ACs", 
            "Lighting Load", "HVAC Load"
        ]
        target = "Energy Consumption"
        
        X = df[features]
        y = df[target]
        
        # Train-Test Split (80% Train, 20% Test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Pipeline Preprocessing
        categorical_features = ["Building"]
        numeric_features = ["Hour", "Temperature", "Humidity", "Occupancy", "Running Computers", "Running ACs", "Lighting Load", "HVAC Load"]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
            ]
        )
        
        # Define candidate models
        models = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=1.0),
            "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
        }
        
        best_r2 = -float("inf")
        
        # Loop through and evaluate
        for name, model in models.items():
            pipeline = Pipeline(steps=[
                ("preprocessor", preprocessor),
                ("regressor", model)
            ])
            
            # Train model
            pipeline.fit(X_train, y_train)
            
            # Predict & Evaluate
            y_pred = pipeline.predict(X_test)
            
            mae = mean_absolute_error(y_test, y_pred)
            rmse = root_mean_squared_error(y_test, y_pred)
            
            # Calculate MAPE safely
            y_test_arr = np.array(y_test)
            y_pred_arr = np.array(y_pred)
            mape = np.mean(np.abs((y_test_arr - y_pred_arr) / np.maximum(1e-5, y_test_arr))) * 100
            
            r2 = r2_score(y_test, y_pred)
            
            self.model_metrics[name] = {
                "MAE": round(mae, 3),
                "RMSE": round(rmse, 3),
                "MAPE (%)": round(mape, 3),
                "R²": round(r2, 4)
            }
            
            # Select best model
            if r2 > best_r2:
                best_r2 = r2
                self.best_model_name = name
                self.best_pipeline = pipeline

        logger.info(f"ML Comparison Complete. Best model: {self.best_model_name} with R²: {best_r2:.4f}")
        
        # Compute feature importances
        self._calculate_feature_importances(X_train)

    def _calculate_feature_importances(self, X_train: pd.DataFrame) -> None:
        """Extracts and normalizes feature importances from the best model."""
        if not self.best_pipeline:
            return
            
        preprocessor = self.best_pipeline.named_steps["preprocessor"]
        regressor = self.best_pipeline.named_steps["regressor"]
        
        # Extract feature names after encoding
        cat_encoder = preprocessor.named_transformers_["cat"]
        cat_features_encoded = cat_encoder.get_feature_names_out(["Building"]).tolist()
        num_features = ["Hour", "Temperature", "Humidity", "Occupancy", "Running Computers", "Running ACs", "Lighting Load", "HVAC Load"]
        
        self.feature_names = num_features + cat_features_encoded
        
        # Get importances or coefficients
        importances = np.zeros(len(self.feature_names))
        if hasattr(regressor, "feature_importances_"):
            importances = regressor.feature_importances_
        elif hasattr(regressor, "coef_"):
            importances = np.abs(regressor.coef_)
        else:
            # Fallback uniform
            importances = np.ones(len(self.feature_names)) / len(self.feature_names)
            
        # Normalize sum to 1
        sum_imp = np.sum(importances)
        if sum_imp > 0:
            importances = importances / sum_imp
            
        self.feature_importances = {name: float(imp) for name, imp in zip(self.feature_names, importances)}

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
        hvac_load: float
    ) -> Dict[str, Any]:
        """Runs interactive scenario prediction and computes deviations from historical averages (FR-4)."""
        if not self.best_pipeline:
            raise ValueError("Model pipeline has not been trained yet.")
            
        # Create input DataFrame matching training columns
        input_data = pd.DataFrame([{
            "Building": building,
            "Hour": hour,
            "Temperature": temp,
            "Humidity": humidity,
            "Occupancy": occupancy,
            "Running Computers": running_computers,
            "Running ACs": running_acs,
            "Lighting Load": lighting_load,
            "HVAC Load": hvac_load
        }])
        
        # Run prediction
        predicted_energy = float(self.best_pipeline.predict(input_data)[0])
        predicted_energy = max(0.1, predicted_energy) # Bound prediction positive
        
        # Calculate dynamic cost and carbon based on settings
        settings = self.data_service.settings_manager.load_settings()
        tariff = settings.get("electricity_tariff")
        carbon_factor = settings.get("carbon_factor")
        
        predicted_cost = predicted_energy * tariff
        predicted_carbon = predicted_energy * carbon_factor
        
        # Compare with historical baseline (Average for this building at this hour)
        df_hist = self.data_service.load_dataset()
        hist_match = df_hist[(df_hist["Building"] == building) & (df_hist["Hour"] == hour)]
        
        if not hist_match.empty:
            baseline_energy = float(hist_match["Energy Consumption"].mean())
        else:
            baseline_energy = float(df_hist[df_hist["Building"] == building]["Energy Consumption"].mean())
            
        diff_energy = predicted_energy - baseline_energy
        pct_change = (diff_energy / baseline_energy) * 100
        
        # Generate explainable AI explanation
        drivers = []
        if running_acs > hist_match["Running ACs"].mean() if not hist_match.empty else False:
            drivers.append("above-average Air Conditioner usage")
        if occupancy > hist_match["Occupancy"].mean() if not hist_match.empty else False:
            drivers.append("higher building occupancy")
        if temp > hist_match["Temperature"].mean() if not hist_match.empty else False:
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
            "explanation": explanation
        }
