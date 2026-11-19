import unittest
from src.maintenance_ai.data_loader import load_data
from src.maintenance_ai.supervisor import SupervisorAgent

class MaintenanceSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sensors, cls.production, cls.maintenance = load_data()
        cls.supervisor = SupervisorAgent(cls.sensors, cls.production, cls.maintenance)

    def test_data_contains_46_turbines(self):
        self.assertEqual(self.production["turbine_id"].nunique(), 46)

    def test_supervisor_returns_all_specialist_outputs(self):
        report = self.supervisor.investigate("WT-03")
        self.assertIn("performance", report)
        self.assertIn("anomalies", report)
        self.assertIn("maintenance", report)
        self.assertIn("summary", report)

    def test_performance_values_are_non_negative(self):
        report = self.supervisor.investigate("WT-03")
        self.assertGreaterEqual(report["performance"]["expected_kwh"], 0)
        self.assertGreaterEqual(report["performance"]["actual_kwh"], 0)

if __name__ == "__main__":
    unittest.main()
