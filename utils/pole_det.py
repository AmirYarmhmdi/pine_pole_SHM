# utils.pole_det.py
# ===========================
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def extract_natural_frequency(
    ax=None, ay=None, az=None, fs=200.0, save_dir="outputs/plots"
):
    """
    Estimate up to three dominant natural frequencies (Hz) from acceleration data.
    - Automatically selects the dominant axis (highest RMS).
    - Displays full signal, 5-second zoom, and FFT in one figure.
    - Returns f1, f2, f3, and plot path.
    """

    # --- Collect available components ---
    components = [c for c in (ax, ay, az) if c is not None]
    labels = ["ax", "ay", "az"]
    available = [labels[i] for i, c in enumerate((ax, ay, az)) if c is not None]
    if not components:
        raise ValueError("No acceleration components provided.")

    # --- Equalize lengths ---
    n = min(len(c) for c in components)
    components = [c[:n] for c in components]

    # --- Pick dominant axis based on RMS ---
    rms_values = [np.sqrt(np.mean(c**2)) for c in components]
    dominant_idx = int(np.argmax(rms_values))
    a_sig = components[dominant_idx]
    axis_used = available[dominant_idx]
    print(
        f"📈 Dominant axis selected: {axis_used} (RMS = {rms_values[dominant_idx]:.3f})"
    )

    # --- Center signal (remove DC bias) ---
    a_sig = a_sig - np.mean(a_sig)

    # --- FFT computation ---
    N = len(a_sig)
    freq = np.fft.rfftfreq(N, d=1 / fs)
    spectrum = np.abs(np.fft.rfft(a_sig))

    # --- Find top 3 frequency peaks (exclude 0 Hz) ---
    spectrum_no_dc = spectrum.copy()
    spectrum_no_dc[0] = 0
    peak_indices = np.argsort(spectrum_no_dc)[-3:][::-1]  # top 3 descending
    freqs_sorted = freq[peak_indices]
    amps_sorted = spectrum_no_dc[peak_indices]
    f1, f2, f3 = freqs_sorted[:3]
    print(f"🎵 Dominant frequencies: f1={f1:.2f} Hz, f2={f2:.2f} Hz, f3={f3:.2f} Hz")

    # --- Save figure ---
    os.makedirs(save_dir, exist_ok=True)
    plot_path = os.path.join(save_dir, "fft_spectrum.png")

    plt.figure(figsize=(10, 8))

    # (1) Full time-domain signal
    plt.subplot(3, 1, 1)
    plt.plot(np.arange(N) / fs, a_sig)
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration [m/s²]")
    plt.title(f"Acceleration Signal ({axis_used} axis) — Full Duration")

    # (2) Zoomed-in 5-second window
    plt.subplot(3, 1, 2)
    t = np.arange(N) / fs
    idx_zoom = t <= 5
    plt.plot(t[idx_zoom], a_sig[idx_zoom])
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration [m/s²]")
    plt.title("Zoomed View (First 5 seconds)")

    # (3) Frequency spectrum
    plt.subplot(3, 1, 3)
    plt.plot(freq, spectrum)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    plt.title("Frequency Spectrum (FFT)")
    colors = ["r", "orange", "green"]
    for i, (f, c) in enumerate(zip(freqs_sorted, colors)):
        plt.axvline(f, color=c, linestyle="--", label=f"f{i+1} = {f:.2f} Hz")
    plt.legend()

    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()

    return (f1, f2, f3), plot_path


def read_sensor_csv(file_path):
    """Read accelerometer data from CSV (timestamp, ax, ay, az)."""
    df = pd.read_csv(file_path)
    cols = df.columns.str.lower()

    def pick(name):
        matches = [i for i, c in enumerate(cols) if name in c]
        return df.iloc[:, matches[0]].values if matches else None

    ax, ay, az = pick("ax"), pick("ay"), pick("az")

    t_matches = [i for i, c in enumerate(cols) if "time" in c]
    timestamps = df.iloc[:, t_matches[0]].values
    fs = 1.0 / np.median(np.diff(timestamps))
    return ax, ay, az, fs
