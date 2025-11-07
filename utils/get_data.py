# utils/get_data.py
# ===========================

import os
from datetime import datetime

import pandas as pd
import requests

DATA_FILE = os.path.join("data", "sensor_data.csv")


def fetch_sensor_data(url="http://localhost:8000/sensor/"):
    """
    Fetch new sensor data from a given URL and append it to sensor_data.csv.

    The endpoint is expected to return a JSON list like:
    [
        {"timestamp": 1730988000.0, "ax": 0.01, "ay": -0.02, "az": 9.81},
        ...
    ]
    """
    print(f"\n🌐 Requesting data from: {url}")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to reach {url}\nError: {e}")
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

    # Convert timestamp if it's not numeric (ISO string)
    if "timestamp" in df_new.columns:
        try:
            df_new["timestamp"] = (
                pd.to_datetime(df_new["timestamp"]).astype(float) / 1e9
            )
        except Exception:
            pass  # assume it's already numeric

    # Save or append
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, mode="a", header=False, index=False)
        print(f"✅ {len(df_new)} new rows appended to {DATA_FILE}")
    else:
        df_new.to_csv(DATA_FILE, index=False)
        print(f"✅ New file created: {DATA_FILE} ({len(df_new)} rows)")

    return True
