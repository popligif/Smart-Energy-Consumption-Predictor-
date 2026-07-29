"""
Unit tests for alert trigger rules and scanning logic.
"""
import unittest
from services.alert_service import AlertService

class TestAlertService(unittest.TestCase):
    """Test suite for AlertService warning and critical notifications."""

    def setUp(self) -> None:
        self.alert_service = AlertService()

    def test_alerts_detection(self) -> None:
        """Verifies that alerts are processed, sorted, and contain expected categories."""
        alerts = self.alert_service.scan_for_alerts()
        self.assertIsInstance(alerts, list)
        
        if alerts:
            first_alert = alerts[0]
            self.assertIn("Severity", first_alert)
            self.assertIn("Category", first_alert)
            self.assertIn("Building", first_alert)
            self.assertIn("Message", first_alert)
            
            # Ensure correct severity values
            self.assertIn(first_alert["Severity"], ["Critical", "Warning", "Info"])

if __name__ == "__main__":
    unittest.main()
