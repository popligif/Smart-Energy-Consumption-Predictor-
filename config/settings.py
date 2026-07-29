"""
Configuration settings manager for loading, updating, and saving campus thresholds and tariffs.
"""
import os
import json
import logging
from typing import Any, Dict
from config import constants

logger = logging.getLogger(__name__)

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

class ConfigSettings:
    """Manages system configuration settings, persisting them in settings.json."""
    
    def __init__(self) -> None:
        self.settings: Dict[str, Any] = {}
        self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Loads settings from JSON or defaults to constants if file doesn't exist."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    self.settings = json.load(f)
                logger.info("Configuration settings loaded successfully from JSON.")
            except Exception as e:
                logger.error(f"Error loading settings file: {e}. Falling back to constants.")
                self.settings = self._get_defaults()
        else:
            self.settings = self._get_defaults()
            self.save_settings(self.settings)
        return self.settings

    def _get_defaults(self) -> Dict[str, Any]:
        """Fetches default parameters from constants.py."""
        return {
            "electricity_tariff": constants.DEFAULT_TARIFF,
            "carbon_factor": constants.DEFAULT_CARBON_FACTOR,
            "power_factor_threshold": constants.POWER_FACTOR_THRESHOLD,
            "hvac_temp_threshold": constants.HVAC_TEMP_LOW_THRESHOLD,
            "peak_load_multiplier": constants.PEAK_LOAD_MULTIPLIER,
            "idle_load_threshold_kw": constants.IDLE_LOAD_THRESHOLD_KW,
            "target_power_factor": constants.TARGET_POWER_FACTOR,
            "eei_benchmark": constants.BUILDING_EEI_BENCHMARK,
        }

    def save_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Saves configuration changes to settings.json."""
        try:
            self.settings.update(new_settings)
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Configuration settings saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def get(self, key: str) -> Any:
        """Helper to get a configuration value."""
        return self.settings.get(key, self._get_defaults().get(key))
