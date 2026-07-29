"""
Service layer for preparing data aggregations and statistical summaries for charts (FR-3).
"""
import pandas as pd
from typing import Dict, Any, List, Tuple
from services.data_service import DataService

class AnalyticsService:
    """Prepares structured data and aggregations for Plotly visualizations."""
    
    def __init__(self) -> None:
        self.data_service = DataService()

    def get_hourly_trends(self) -> pd.DataFrame:
        """Aggregates energy consumption by hour and building for time-series trends."""
        df = self.data_service.load_dataset()
        # Pivot table: Index = Hour, Columns = Building, Values = Energy Consumption
        pivot_df = df.pivot_table(
            index="Hour", 
            columns="Building", 
            values="Energy Consumption", 
            aggfunc="mean"
        ).reset_index()
        return pivot_df

    def get_building_comparison_data(self) -> pd.DataFrame:
        """Computes summary metrics for side-by-side building comparisons."""
        df = self.data_service.load_dataset()
        summary = df.groupby("Building").agg(
            Total_Energy_kWh=("Energy Consumption", "sum"),
            Peak_Power_kW=("Current Power (kW)", "max"),
            Average_Occupancy=("Occupancy", "mean"),
            Total_Cost_INR=("Dynamic Cost (INR)", "sum"),
            Total_Carbon_kg=("Dynamic Carbon (kg CO2)", "sum")
        ).reset_index()
        return summary

    def get_correlation_matrix(self) -> Tuple[pd.DataFrame, List[str]]:
        """Computes correlation coefficients between numeric energy and environmental factors."""
        df = self.data_service.load_dataset()
        numerical_cols = [
            "Energy Consumption", "Temperature", "Humidity", "Occupancy", 
            "Running ACs", "Running Computers", "Lighting Load", "HVAC Load", 
            "Voltage", "Current", "Power Factor", "Rainfall"
        ]
        # Filter existing columns
        cols_to_use = [col for col in numerical_cols if col in df.columns]
        corr_df = df[cols_to_use].corr()
        return corr_df, cols_to_use

    def get_weather_load_data(self) -> pd.DataFrame:
        """Aggregates load profile vs weather parameters."""
        df = self.data_service.load_dataset()
        return df[["Temperature", "Humidity", "Energy Consumption", "Building", "Hour", "Weather Condition"]]

    def get_power_factor_analysis(self) -> pd.DataFrame:
        """Returns power factor records grouped by building and hour."""
        df = self.data_service.load_dataset()
        return df[["Hour", "Building", "Power Factor", "Voltage", "Current"]]
