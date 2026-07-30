"""
Data Access Layer (DAL) Service for loading, caching, validating, and feature engineering.
"""
import os
import pandas as pd
import logging
import streamlit as st
from typing import Optional
from config.settings import ConfigSettings

logger = logging.getLogger(__name__)

# Locate dataset path relative to root workspace
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DEFAULT_CSV_PATH = os.path.join(DATA_DIR, "miet_campus_dataset.csv")


@st.cache_data(show_spinner="Loading dataset...", ttl=600)
def _load_and_process_csv(csv_path: str) -> pd.DataFrame:
    """
    Standalone cached function to load and process CSV data.
    Using @st.cache_data (module-level) so it is cached across all reruns.
    """
    settings_manager = ConfigSettings()
    settings = settings_manager.load_settings()
    tariff = settings.get("electricity_tariff")
    carbon_factor = settings.get("carbon_factor")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at critical path: {csv_path}")

    df = pd.read_csv(csv_path)

    # --- Schema validation ---
    required_cols = [
        "Timestamp", "Hour", "Building", "Energy Consumption", "Temperature",
        "Humidity", "Occupancy", "Running ACs", "Running Computers",
        "Power Factor", "Voltage", "Current", "Daily Cost", "Carbon Emission"
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Invalid dataset schema! Missing columns: {missing_cols}")

    # --- Data cleansing & conversions ---
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # --- Feature engineering ---
    df["Dynamic Cost (INR)"] = df["Energy Consumption"] * tariff
    df["Dynamic Carbon (kg CO2)"] = df["Energy Consumption"] * carbon_factor

    df["Occupants"] = df["Occupancy"].apply(lambda x: max(1, x))
    df["Consumption Per Occupant (kWh)"] = df["Energy Consumption"] / df["Occupants"]

    df["Students_Max_1"] = df["Students"].apply(lambda x: max(1, x))
    df["Student_Computer_Ratio"] = df["Running Computers"] / df["Students_Max_1"]

    df["Load Type"] = df["Hour"].apply(lambda h: "Peak" if 9 <= h <= 17 else "Off-Peak")

    logger.info("Dataset successfully loaded and cached in memory.")
    return df


class DataService:
    """Singleton service for dataset ingestion and data modeling."""

    _instance: Optional["DataService"] = None

    def __new__(cls, *args, **kwargs) -> "DataService":
        if not cls._instance:
            cls._instance = super(DataService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, csv_path: str = DEFAULT_CSV_PATH) -> None:
        # Prevent re-initialization in singleton
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.csv_path = csv_path
        self.settings_manager = ConfigSettings()
        self._initialized = True

    def load_dataset(self, force_reload: bool = False) -> pd.DataFrame:
        """Ingests the CSV dataset via the Streamlit-cached loader."""
        if force_reload:
            _load_and_process_csv.clear()
        return _load_and_process_csv(self.csv_path)

    def get_building_list(self) -> list:
        """Returns the unique list of buildings in the dataset."""
        df = self.load_dataset()
        return sorted(df["Building"].unique().tolist())
