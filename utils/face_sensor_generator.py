# face_sensor_generator.py
# ===========================
import os

import numpy as np
import pandas as pd

# === Settings ===
fs = 200  # Sampling frequency [Hz]
duration = 60  # Total time [s] → 60 s × 200 Hz = 12 000 samples
f_true = 2.18  # True vibration frequency [Hz]
noise_level = 0.05  # Small random noise amplitude

# === Generate time vector ===
t = np.arange(0, duration, 1 / fs)

# === Generate synthetic acceleration signals (3 axes) ===
ax = 0.8 * np.sin(2 * np.pi * f_true * t) + noise_level * np.random.randn(len(t))
ay = 0.6 * np.sin(2 * np.pi * f_true * t + np.pi / 6) + noise_level * np.random.randn(
    len(t)
)
az = 0.4 * np.sin(2 * np.pi * f_true * t + np.pi / 3) + noise_level * np.random.randn(
    len(t)
)

# === Combine into DataFrame ===
df = pd.DataFrame(
    {
        "timestamp": np.round(t, 3),
        "ax": np.round(ax, 3),
        "ay": np.round(ay, 3),
        "az": np.round(az, 3),
    }
)

# === Save to CSV ===
os.makedirs("data", exist_ok=True)
file_path = os.path.join("data", "sensor_data.csv")
df.to_csv(file_path, index=False)

print(f"✅ Synthetic sensor data generated → {file_path}")
print(f"Samples: {len(df)}, Duration: {duration}s, True frequency: {f_true} Hz")
