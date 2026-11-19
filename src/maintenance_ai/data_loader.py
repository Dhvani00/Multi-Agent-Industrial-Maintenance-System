from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

def load_data():
    """Load the bundled synthetic CSV files."""
    sensors = pd.read_csv(DATA_DIR / "sensor_readings.csv", parse_dates=["timestamp"])
    production = pd.read_csv(DATA_DIR / "production.csv", parse_dates=["date"])
    maintenance = pd.read_csv(DATA_DIR / "maintenance_records.csv", parse_dates=["date"])
    return sensors, production, maintenance
