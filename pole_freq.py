import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def extract_natural_frequency(ax, ay, az, fs, plot=True):
    """
    Estimate the dominant (natural) frequency from 3-axis acceleration data.
    """
    n = min(len(ax), len(ay), len(az))
    ax, ay, az = ax[:n], ay[:n], az[:n]
    a_mag = np.sqrt(ax**2 + ay**2 + az**2)
    a_mag -= np.mean(a_mag)

    N = len(a_mag)
    freq = np.fft.rfftfreq(N, d=1 / fs)
    spectrum = np.abs(np.fft.rfft(a_mag))

    idx_peak = np.argmax(spectrum[1:]) + 1
    f_nat = freq[idx_peak]

    if plot:
        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        plt.plot(np.arange(N) / fs, a_mag)
        plt.title("Acceleration Magnitude (Time Domain)")
        plt.xlabel("Time [s]")
        plt.ylabel("Acceleration [m/s²]")

        plt.subplot(1, 2, 2)
        plt.plot(freq, spectrum)
        plt.title("Frequency Spectrum (FFT)")
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Amplitude")
        plt.axvline(f_nat, color="r", linestyle="--", label=f"f = {f_nat:.2f} Hz")
        plt.legend()
        plt.tight_layout()
        plt.show()

    return f_nat


def read_sensor_csv(file_path):
    """
    Read CSV file containing timestamp and 3-axis acceleration data.
    Columns required: timestamp, ax, ay, az
    """
    df = pd.read_csv(file_path)
    if not {"timestamp", "ax", "ay", "az"}.issubset(df.columns):
        raise ValueError("CSV must contain columns: timestamp, ax, ay, az")

    timestamps = df["timestamp"].values
    ax, ay, az = df["ax"].values, df["ay"].values, df["az"].values

    # Estimate sampling frequency from timestamps
    dt = np.median(np.diff(timestamps))
    fs = 1.0 / dt

    print(f"Detected sampling frequency: {fs:.2f} Hz")
    return ax, ay, az, fs


if __name__ == "__main__":
    print("=== Frequency Extraction from 3-Axis Accelerometer ===")
    file_path = input("Enter CSV file path (e.g., sensor_data.csv): ").strip()

    try:
        ax, ay, az, fs = read_sensor_csv(file_path)
        f_nat = extract_natural_frequency(ax, ay, az, fs, plot=True)
        print(f"\nEstimated natural frequency: {f_nat:.2f} Hz")

    except Exception as e:
        print(f"❌ Error: {e}")