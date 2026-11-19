import json
from .agents import PerformanceAgent, AnomalyAgent, MaintenanceAgent
from .llm import synthesize_with_llm

class SupervisorAgent:
    """Coordinates specialist agents and assembles a single investigation."""

    def __init__(self, sensors, production, maintenance, use_llm=False):
        from .retrieval import MaintenanceRetriever
        self.performance_agent = PerformanceAgent(production)
        self.anomaly_agent = AnomalyAgent(sensors)
        self.maintenance_agent = MaintenanceAgent(MaintenanceRetriever(maintenance))
        self.use_llm = use_llm

    def investigate(self, turbine_id, question=None):
        question = question or f"Investigate maintenance and performance for {turbine_id}"
        performance = self.performance_agent.run(turbine_id)
        anomalies = self.anomaly_agent.run(turbine_id)
        maintenance = self.maintenance_agent.run(
            turbine_id,
            query="gearbox temperature vibration lubrication inspection bearing maintenance"
        )
        evidence = {
            "turbine_id": turbine_id,
            "performance_findings": performance,
            "sensor_anomaly_findings": anomalies,
            "retrieved_maintenance_records": maintenance,
        }
        llm_report = synthesize_with_llm(question, json.dumps(evidence, indent=2)) if self.use_llm else None
        report = {
            "title": f"Investigation report: {turbine_id}",
            "question": question,
            "performance": performance,
            "anomalies": anomalies,
            "maintenance": maintenance,
            "llm_summary": llm_report,
            "summary": self._deterministic_summary(performance, anomalies, maintenance),
            "disclaimer": (
                "Synthetic demonstration data. Statistical flags are not confirmed faults. "
                "All maintenance decisions require qualified human review."
            ),
        }
        return report

    @staticmethod
    def _deterministic_summary(performance, anomalies, maintenance):
        if "error" in performance:
            return performance["error"]
        gap = performance["production_gap_kwh"]
        pct = performance["below_expected_percent"]
        count = anomalies.get("anomaly_count", 0)
        records = maintenance.get("retrieved_count", 0)
        return (
            f"Across {performance['period_days']} daily production records, actual output was "
            f"{performance['actual_kwh']:,.1f} kWh versus {performance['expected_kwh']:,.1f} kWh expected "
            f"(gap: {gap:,.1f} kWh; {pct:.2f}% below expected). The statistical screening flagged "
            f"{count} sensor observations and retrieved {records} potentially relevant maintenance records. "
            "These findings can guide investigation but do not establish a root cause."
        )
