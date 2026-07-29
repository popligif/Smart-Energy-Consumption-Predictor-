"""
Unit tests for ML regression models and scenario predictions.
"""
import unittest
from services.ml_service import MLService

class TestMLService(unittest.TestCase):
    """Test suite for MLService training and scenario planning model."""

    def setUp(self) -> None:
        self.ml_service = MLService()

    def test_training_completes(self) -> None:
        """Verifies that ML training runs and selects a best model with valid metrics."""
        metrics = self.ml_service.get_comparison_metrics()
        self.assertIsNotNone(self.ml_service.best_model_name)
        self.assertIn(self.ml_service.best_model_name, metrics)
        
        # Verify metric structure
        best_metrics = metrics[self.ml_service.best_model_name]
        self.assertIn("R²", best_metrics)
        self.assertIn("MAE", best_metrics)

    def test_predict_scenario(self) -> None:
        """Verifies that predicted load increases or decreases logically with input modifications."""
        # Run baseline prediction
        pred_base = self.ml_service.predict_scenario(
            building="Academic Block A",
            hour=12,
            temp=28.0,
            humidity=60.0,
            occupancy=20,
            running_acs=2,
            running_computers=15,
            lighting_load=1.5,
            hvac_load=3.0
        )
        
        # Run high-load prediction
        pred_high = self.ml_service.predict_scenario(
            building="Academic Block A",
            hour=12,
            temp=38.0,
            humidity=80.0,
            occupancy=100,
            running_acs=10,
            running_computers=80,
            lighting_load=4.0,
            hvac_load=15.0
        )
        
        self.assertGreater(pred_high["predicted_energy_kw"], pred_base["predicted_energy_kw"])
        self.assertGreater(pred_high["predicted_cost_inr"], pred_base["predicted_cost_inr"])
        self.assertIsNotNone(pred_high["explanation"])

if __name__ == "__main__":
    unittest.main()
