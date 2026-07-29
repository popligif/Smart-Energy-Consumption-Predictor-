"""
Data Access Layer (DAL) Service for loading, caching, validating, and feature engineering.
"""
import os
import pandas as pd
import logging
from typing import Optional
from config.settings import ConfigSettings

logger = logging.getLogger(__name__)

# Locate dataset path relative to root workspace
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DEFAULT_CSV_PATH = os.path.join(DATA_DIR, "miet_campus_dataset.csv")

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
        self._df: Optional[pd.DataFrame] = None
        self._initialized = True

    def load_dataset(self, force_reload: bool = False) -> pd.DataFrame:
        """Ingests the CSV dataset, runs validator checks, and applies feature engineering."""
        if self._df is not None and not force_reload:
            return self._df
            
        if not os.path.exists(self.csv_path):
            error_msg = f"Dataset not found at critical path: {self.csv_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        try:
            df = pd.read_csv(self.csv_path)
            self._validate_schema(df)
            
            # Data cleansing & conversions
            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            
            # Apply dynamic feature engineering
            df = self._run_feature_engineering(df)
            
            self._df = df
            logger.info("Dataset successfully loaded and cached in memory.")
            return self._df
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise

    def _validate_schema(self, df: pd.DataFrame) -> None:
        """Enforces critical columns validation to check dataset schema consistency (FR-1)."""
        required_cols = [
            "Timestamp", "Hour", "Building", "Energy Consumption", "Temperature", 
            "Humidity", "Occupancy", "Running ACs", "Running Computers", 
            "Power Factor", "Voltage", "Current", "Daily Cost", "Carbon Emission"
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            error_msg = f"Invalid dataset schema! Missing columns: {missing_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _run_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Injects custom features and calibrated financial/carbon metrics (FR-1)."""
        settings = self.settings_manager.load_settings()
        tariff = settings.get("electricity_tariff")
        carbon_factor = settings.get("carbon_factor")
        
        # Recalculate metrics based on current configurations
        df["Dynamic Cost (INR)"] = df["Energy Consumption"] * tariff
        df["Dynamic Carbon (kg CO2)"] = df["Energy Consumption"] * carbon_factor
        
        # Building Performance Indicators
        # Avoid zero divisions for occupancy metrics
        df["Occupants"] = df["Occupancy"].apply(lambda x: max(1, x))
        df["Consumption Per Occupant (kWh)"] = df["Energy Consumption"] / df["Occupants"]
        
        # Computing student-to-computer ratio
        df["Students_Max_1"] = df["Students"].apply(lambda x: max(1, x))
        df["Student_Computer_Ratio"] = df["Running Computers"] / df["Students_Max_1"]
        
        # Categorizing load periods
        df["Load Type"] = df["Hour"].apply(lambda h: "Peak" if 9 <= h <= 17 else "Off-Peak")
        
        return df

    def get_building_list(self) -> list:
        """Returns the unique list of buildings in the dataset."""
        df = self.load_dataset()
        return sorted(df["Building"].unique().tolist())
