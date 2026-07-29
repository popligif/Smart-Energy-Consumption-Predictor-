"""
Unit tests for data service loading, schema validation, and feature engineering.
"""
import unittest
import pandas as pd
from services.data_service import DataService

class TestDataService(unittest.TestCase):
    """Test suite for DataService functionality."""

    def setUp(self) -> None:
        self.data_service = DataService()

    def test_singleton(self) -> None:
        """Verifies that DataService follows the Singleton design pattern."""
        service_instance_two = DataService()
        self.assertIs(self.data_service, service_instance_two)

    def test_load_dataset(self) -> None:
        """Verifies that the dataset loads into a non-empty DataFrame with custom columns."""
        df = self.data_service.load_dataset()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        
        # Check engineered features exist
        self.assertIn("Dynamic Cost (INR)", df.columns)
        self.assertIn("Dynamic Carbon (kg CO2)", df.columns)
        self.assertIn("Consumption Per Occupant (kWh)", df.columns)
        self.assertIn("Load Type", df.columns)

    def test_get_building_list(self) -> None:
        """Verifies unique building names list contains expected blocks."""
        buildings = self.data_service.get_building_list()
        self.assertIn("Academic Block A", buildings)
        self.assertIn("Workshop Building", buildings)
        self.assertEqual(len(buildings), 6)

if __name__ == "__main__":
    unittest.main()
