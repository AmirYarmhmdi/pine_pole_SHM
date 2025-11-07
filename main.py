# main.py
import json
import os
from datetime import datetime

import numpy as np

from utils.get_data import fetch_sensor_data
# === Local imports ===
from utils.pole_det import extract_natural_frequency, read_sensor_csv
from utils.pole_est import (height_from_circumference, natural_frequency,
                            print_material_assumptions)

# === Paths ===
DATA_FILE = os.path.join("data", "sensor_data.csv")
OUTPUT_DIR = os.path.join("outputs")
PLOT_DIR = os.path.join(OUTPUT_DIR, "plots")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "results.json")
CONFIG_FILE = os.path.join("config", "config.json")

os.makedirs(PLOT_DIR, exist_ok=True)

# === Load configuration (thresholds + material/cable info) ===
with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)
THR = CONFIG.get(
    "thresholds", {"minor_max": 5.0, "moderate_max": 15.0, "severe_min": 20.0}
)


def append_json_record(record, path):
    """Append new results to JSON file."""
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if not isinstance(data, list):
                data = [data]
        except (json.JSONDecodeError, FileNotFoundError):
            data = []
    else:
        data = []
    data.append(record)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def main():
    print("\n=== WoodSense Pole Frequency Comparison ===")

    # Step 0 — Ask if new data should be fetched
    choice = (
        input("\n🌐 Do you want to fetch new sensor data from API? (y/n): ")
        .strip()
        .lower()
    )
    if choice == "y":
        url = input(
            "Enter local sensor URL (default: http://localhost:8000/sensor/): "
        ).strip()
        if not url:
            url = "http://localhost:8000/sensor/"
        fetch_sensor_data(url)
    else:
        print(f"📁 Using existing data file: {DATA_FILE}")

    # Step 1 — Print assumptions
    print_material_assumptions()

    # Step 2 — Ask for geometry input
    print("\nPlease provide one of the following:")
    print("1️⃣  Measured circumference of the pole at ground level (m)")
    print("2️⃣  Height of the pole above ground (m)")

    mode = input("Select input type (1 or 2): ").strip()

    # Physical bounds
    C_min = np.pi * 0.170  # 0.534 m
    C_max = np.pi * 0.249375  # 0.783 m
    L_min, L_max = 0.5, 9.0

    if mode == "1":
        try:
            C_ground = float(
                input("Enter measured pole circumference at ground level (m): ").strip()
            )
        except ValueError:
            print("❌ Invalid numeric input for circumference.")
            return

        if not (C_min <= C_ground <= C_max):
            print(
                f"❌ Invalid circumference value. Must be between {C_min:.3f} m and {C_max:.3f} m."
            )
            return

        L_free = height_from_circumference(C_ground)
        print(f"📏 Estimated height above ground: {L_free:.2f} m")

    elif mode == "2":
        try:
            L_free = float(input("Enter height above ground (m): ").strip())
        except ValueError:
            print("❌ Invalid numeric input for height.")
            return

        if not (L_min <= L_free <= L_max):
            print(
                f"❌ Invalid height value. Must be between {L_min:.1f} m and {L_max:.1f} m."
            )
            return

        print(f"📏 Using provided height above ground: {L_free:.2f} m")
        C_ground = None
    else:
        print("❌ Invalid selection. Please choose 1 or 2.")
        return

    # Step 3 — Read accelerometer data
    print("\n📥 Loading accelerometer data...")
    ax, ay, az, fs = read_sensor_csv(DATA_FILE)
    print(f"✅ Data loaded. Sampling frequency detected: {fs:.2f} Hz")

    # Step 4 — Extract frequencies
    print("\n🔍 Extracting natural frequencies (FFT analysis)...")
    (f1, f2, f3), plot_path = extract_natural_frequency(
        ax, ay, az, fs, save_dir=PLOT_DIR
    )
    f_measured = f1
    print(f"📡 Mode 1 Frequency (Measured): {f_measured:.2f} Hz")
    print(f"🎵 Higher modes: f2={f2:.2f} Hz, f3={f3:.2f} Hz")
    print(f"📊 Spectrum plot saved at: {plot_path}")

    # Step 5 — Theoretical frequency
    f_theoretical = natural_frequency(L_free)
    diff_percent = ((f_measured - f_theoretical) / f_theoretical) * 100

    print("\n🧮 Analytical model results:")
    print(f"  Theoretical frequency: {f_theoretical:.2f} Hz")
    print(f"  Measured frequency:    {f_measured:.2f} Hz")
    print(f"  Difference:            {diff_percent:+.2f}%")

    # Step 6 — Damage level interpretation
    if abs(diff_percent) <= THR["minor_max"]:
        level = "Minor"
        condition = "Minor deviation — likely surface or environmental variation."
        action = "No immediate action; continue periodic monitoring."
    elif abs(diff_percent) <= THR["moderate_max"]:
        level = "Moderate"
        condition = (
            "Moderate stiffness reduction — possible internal decay or cracking."
        )
        action = "Inspect the pole; consider local repair or reinforcement."
    elif abs(diff_percent) >= THR["severe_min"]:
        level = "Severe"
        condition = "Severe frequency drop — significant structural deterioration."
        action = "Immediate replacement or major intervention required."
    else:
        level = "Unclassified"
        condition = "Frequency deviation outside defined thresholds."
        action = "Verify measurements or review model assumptions."

    print(f"\n⚠️ Condition: {condition}")
    print(f"🛠️ Suggested Action: {action}")

    # Step 7 — Save results
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sensor_data_file": DATA_FILE,
        "plot_file": plot_path,
        "input_type": "circumference" if mode == "1" else "height",
        "C_ground_m": C_ground,
        "L_free_m": round(L_free, 2),
        "fs_Hz": round(fs, 2),
        "f_theoretical_Hz": round(f_theoretical, 3),
        "f_measured_Hz": round(f_measured, 3),
        "difference_percent": round(diff_percent, 2),
        "damage_level": level,
        "condition": condition,
        "recommended_action": action,
        "modes": {"f1_Hz": round(f1, 3), "f2_Hz": round(f2, 3), "f3_Hz": round(f3, 3)},
    }

    append_json_record(record, RESULTS_FILE)
    print(f"\n💾 Result appended to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
