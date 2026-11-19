import pandas as pd
import numpy as np

class PerformanceAgent:
    name = "Performance Agent"

    def __init__(self, production_df):
        self.data = production_df

    def run(self, turbine_id):
        df = self.data[self.data["turbine_id"] == turbine_id].copy()
        if df.empty:
            return {"agent": self.name, "error": f"No production records for {turbine_id}."}
        expected = float(df["expected_kwh"].sum())
        actual = float(df["actual_kwh"].sum())
        gap = expected - actual
        deviation = (gap / expected * 100) if expected else 0.0
        return {
            "agent": self.name,
            "turbine_id": turbine_id,
            "period_days": int(len(df)),
            "expected_kwh": round(expected, 1),
            "actual_kwh": round(actual, 1),
            "production_gap_kwh": round(gap, 1),
            "below_expected_percent": round(deviation, 2),
            "daily_records": len(df),
        }


class AnomalyAgent:
    name = "Anomaly Detection Agent"

    def __init__(self, sensor_df, threshold=2.5, window=12):
        self.data = sensor_df
        self.threshold = threshold
        self.window = window

    def run(self, turbine_id, top_k=8):
        df = self.data[self.data["turbine_id"] == turbine_id].copy()
        if df.empty:
            return {"agent": self.name, "error": f"No sensor records for {turbine_id}.", "anomalies": []}
        findings = []
        for sensor in ["gearbox_temp_c", "vibration_mm_s", "wind_speed_ms"]:
            series = df[sensor].astype(float)
            rolling_mean = series.rolling(self.window, min_periods=max(4, self.window // 3)).mean()
            rolling_std = series.rolling(self.window, min_periods=max(4, self.window // 3)).std().replace(0, np.nan)
            z = ((series - rolling_mean) / rolling_std).replace([np.inf, -np.inf], np.nan)
            flagged = df.loc[z.abs() > self.threshold].copy()
            flagged["_z"] = z.loc[flagged.index]
            for _, row in flagged.iterrows():
                findings.append({
                    "timestamp": str(row["timestamp"]),
                    "sensor": sensor,
                    "value": round(float(row[sensor]), 2),
                    "rolling_z_score": round(float(row["_z"]), 2),
                    "threshold": self.threshold,
                })
        findings.sort(key=lambda x: abs(x["rolling_z_score"]), reverse=True)
        return {
            "agent": self.name,
            "turbine_id": turbine_id,
            "method": f"Rolling Z-score (window={self.window}, threshold={self.threshold})",
            "anomaly_count": len(findings),
            "anomalies": findings[:top_k],
            "note": "Statistical flags indicate unusual values, not confirmed faults.",
        }


class MaintenanceAgent:
    name = "Maintenance Retrieval Agent"

    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, turbine_id, query=None):
        query = query or "gearbox vibration temperature lubrication inspection maintenance"
        records = self.retriever.search(query, turbine_id=turbine_id, top_k=5)
        return {
            "agent": self.name,
            "turbine_id": turbine_id,
            "query": query,
            "retrieved_count": len(records),
            "records": records,
            "method": "TF-IDF similarity retrieval",
        }
