# ============================================================
# utils/get_data.py
# Fetch and store sensor data from configurable API endpoint
# ============================================================

import os
from datetime import datetime

import pandas as pd
import requests

from utils.config_loader import load_config

# Load configuration
CONFIG = load_config()
DATA_CFG = CONFIG.get("data_source", {})
DATA_FILE = DATA_CFG.get("save_path", os.path.join("data", "sensor_data.csv"))
API_URL_DEFAULT = DATA_CFG.get("api_url", "http://localhost:8000/sensor/")


def fetch_sensor_data(url=None):
    """
    Fetch new sensor data from the configured or provided API endpoint
    and append it to the CSV file defined in config.json.

    The endpoint is expected to return JSON like:
    [
        {"timestamp": 1730988000.0, "ax": 0.01, "ay": -0.02, "az": 9.81},
        ...
    ]
    """
    api_url = url or API_URL_DEFAULT
    print(f"\n🌐 Requesting sensor data from: {api_url}")

    try:
        response = requests.get(api_url, timeout=8)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to reach {api_url}\nError: {e}")
        return False

    try:
        data = response.json()
    except Exception:
        print("❌ Server response is not valid JSON.")
        return False

    if not isinstance(data, list) or len(data) == 0:
        print("⚠️ No valid data received from endpoint.")
        return False

    # Convert JSON to DataFrame
    df_new = pd.DataFrame(data)

    # Normalize timestamps
    if "timestamp" in df_new.columns:
        if not pd.api.types.is_numeric_dtype(df_new["timestamp"]):
            try:
                df_new["timestamp"] = (
                    pd.to_datetime(df_new["timestamp"]).astype(float) / 1e9
                )
            except Exception:
                print("⚠️ Could not convert timestamps — leaving as-is.")

    # Save or append
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    write_mode = "a" if os.path.exists(DATA_FILE) else "w"
    header = not os.path.exists(DATA_FILE)
    df_new.to_csv(DATA_FILE, mode=write_mode, header=header, index=False)
    print(
        f"✅ {len(df_new)} rows {'appended to' if not header else 'saved in'} {DATA_FILE}"
    )

    return True


# Optional standalone test
if __name__ == "__main__":
    fetch_sensor_data()
