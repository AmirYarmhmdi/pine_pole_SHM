# ============================================================
# main.py
# Main controller for WoodSense Project
# Supports: Free poles and poles with lateral support (guyed)
# ============================================================

import json
import os
from datetime import datetime

import numpy as np

from utils.config_loader import load_config
from utils.get_data import fetch_sensor_data
# === Local imports ===
from utils.pole_det import extract_natural_frequency, read_sensor_csv
from utils.pole_est import (height_from_circumference, natural_frequency,
                            natural_frequency_with_support,
                            print_material_assumptions)

# === Paths ===
DATA_FILE = os.path.join("data", "sensor_data.csv")
OUTPUT_DIR = os.path.join("outputs")
PLOT_DIR = os.path.join(OUTPUT_DIR, "plots")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "results.json")

os.makedirs(PLOT_DIR, exist_ok=True)

# === Load configuration ===
CONFIG = load_config()
THR = CONFIG.get(
    "thresholds", {"minor_max": 5.0, "moderate_max": 15.0, "severe_min": 20.0}
)

# ============================================================
# Helper function to append results
# ============================================================


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


# ============================================================
# Main Workflow
# ============================================================


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

    # Step 1 — Material & cable info
    print_material_assumptions()

    # Step 2 — Ask if pole has lateral support
    has_support = (
        input("\n🪵 Does this pole have a lateral support (guy)? (y/n): ")
        .strip()
        .lower()
    )
    h_support = None
    if has_support == "y":
        try:
            h_support = float(
                input("Enter height of support connection above ground (m): ").strip()
            )
        except ValueError:
            print("❌ Invalid numeric value for support height.")
            h_support = None

    # Step 3 — Input geometry type
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
                f"❌ Invalid circumference. Must be between {C_min:.3f} m and {C_max:.3f} m."
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
                f"❌ Invalid height. Must be between {L_min:.1f} m and {L_max:.1f} m."
            )
            return
        C_ground = None
        print(f"📏 Using provided height above ground: {L_free:.2f} m")

    else:
        print("❌ Invalid selection. Please choose 1 or 2.")
        return

    # Step 4 — Load sensor data
    print("\n📥 Loading accelerometer data...")
    ax, ay, az, fs = read_sensor_csv(DATA_FILE)
    print(f"✅ Data loaded. Sampling frequency detected: {fs:.2f} Hz")

    # Step 5 — FFT Analysis
    print("\n🔍 Extracting natural frequencies (FFT analysis)...")
    (f1, f2, f3), plot_path = extract_natural_frequency(
        ax, ay, az, fs, save_dir=PLOT_DIR
    )
    f_peaks = [f1, f2, f3]
    print("📡 FFT dominant peaks:", [f"{f:.2f}" for f in f_peaks])
    print(f"📊 Plot saved at: {plot_path}")

    # Step 6 — Analytical frequencies
    f_free = natural_frequency(L_free)
    f_support = None
    if has_support == "y" and h_support and h_support > 0:
        f_support = natural_frequency_with_support(L_free, h_support)

    # Step 7 — Compare with FFT peaks
    def closest_peak(target):
        return (
            min(f_peaks, key=lambda f: abs(f - target))
            if not np.isnan(target)
            else np.nan
        )

    match_free = closest_peak(f_free)
    match_support = closest_peak(f_support) if f_support else None

    # Step 8 — Display results
    print("\n🧮 Analytical Model Results:")
    print(
        f"  Theoretical free-side frequency: {f_free:.2f} Hz | Closest FFT peak: {match_free:.2f} Hz"
    )
    if f_support:
        print(
            f"  Theoretical supported-side frequency: {f_support:.2f} Hz | Closest FFT peak: {match_support:.2f} Hz"
        )

    # Step 9 — Compute difference & health classification
    if f_support:
        diff_percent = ((match_support - f_support) / f_support) * 100
        diff_label = "supported-side"
    else:
        diff_percent = ((match_free - f_free) / f_free) * 100
        diff_label = "free-side"

    if abs(diff_percent) <= THR["minor_max"]:
        level = "Minor"
        condition = "Minor deviation — likely environmental variation."
        action = "No action needed; continue routine monitoring."
    elif abs(diff_percent) <= THR["moderate_max"]:
        level = "Moderate"
        condition = (
            "Moderate stiffness loss — possible internal decay or local cracking."
        )
        action = "Inspect the pole or support; plan preventive maintenance."
    elif abs(diff_percent) >= THR["severe_min"]:
        level = "Severe"
        condition = "Severe stiffness loss — structural degradation likely."
        action = "Immediate inspection and possible replacement required."
    else:
        level = "Unclassified"
        condition = "Frequency deviation outside standard thresholds."
        action = "Review boundary conditions or sensor calibration."

    print(f"\n📊 Mode analyzed: {diff_label}")
    print(f"Difference: {diff_percent:+.2f}% | Damage Level: {level}")
    print(f"⚠️ Condition: {condition}")
    print(f"🛠️ Suggested Action: {action}")

    # Step 10 — Save result (structured JSON format)
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": {
            "sensor_data_file": DATA_FILE,
            "plot_file": plot_path,
            "input_type": "circumference" if mode == "1" else "height",
            "C_ground_m": C_ground,
            "L_free_m": round(L_free, 2),
            "has_support": has_support == "y",
            "support_height_m": h_support,
            "fs_Hz": round(fs, 2),
            "fft_peaks_Hz": [round(p, 3) for p in f_peaks],
        },
        "theoretical": {
            "free": {"frequency_Hz": round(f_free, 3)},
            "supported": {"frequency_Hz": round(f_support, 3) if f_support else None},
        },
        "fft_analysis": {
            "matched_free": {
                "frequency_Hz": round(match_free, 3),
                "difference_percent": round(((match_free - f_free) / f_free) * 100, 2),
            },
            "matched_support": {
                "frequency_Hz": round(match_support, 3) if f_support else None,
                "difference_percent": (
                    round(((match_support - f_support) / f_support) * 100, 2)
                    if f_support
                    else None
                ),
            },
        },
        "diagnosis": {
            "damage_level": level,
            "condition_summary": condition,
            "recommended_action": action,
        },
    }

    append_json_record(record, RESULTS_FILE)
    print(f"\n💾 Analytical results appended to: {RESULTS_FILE}")


# ============================================================
# Run main
# ============================================================

if __name__ == "__main__":
    main()
