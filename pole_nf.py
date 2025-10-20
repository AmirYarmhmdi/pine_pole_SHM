import matplotlib.pyplot as plt
import numpy as np


def extract_natural_frequency(ax, ay, az, fs, plot=True):
    """
    Estimate the natural frequency from 3-axis acceleration data.

    Parameters:
        ax, ay, az : np.ndarray
            Acceleration signals in m/s² for X, Y, Z directions.
        fs : float
            Sampling frequency in Hz.
        plot : bool
            If True, plots the acceleration magnitude and FFT spectrum.

    Returns:
        f_nat : float
            Dominant (natural) frequency in Hz.
    """

    # Ensure equal length
    n = min(len(ax), len(ay), len(az))
    ax, ay, az = ax[:n], ay[:n], az[:n]

    # Compute acceleration magnitude (vector sum)
    a_mag = np.sqrt(ax**2 + ay**2 + az**2)

    # Remove DC offset
    a_mag -= np.mean(a_mag)

    # FFT computation
    N = len(a_mag)
    freq = np.fft.rfftfreq(N, d=1 / fs)
    spectrum = np.abs(np.fft.rfft(a_mag))

    # Find dominant frequency (excluding 0 Hz)
    idx_peak = np.argmax(spectrum[1:]) + 1
    f_nat = freq[idx_peak]

    # Optional plots
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


# -------------------- Example usage --------------------
if __name__ == "__main__":
    # Simulate synthetic 3-axis vibration data
    fs = 200.0  # sampling rate (Hz)
    t = np.linspace(0, 10, int(10 * fs))  # 10 seconds of data
    f_true = 4.5  # true natural frequency (Hz)

    # Create sinusoidal vibration with some noise
    ax = 0.5 * np.sin(2 * np.pi * f_true * t) + 0.05 * np.random.randn(len(t))
    ay = 0.3 * np.sin(2 * np.pi * f_true * t + np.pi / 4) + 0.05 * np.random.randn(
        len(t)
    )
    az = 0.2 * np.sin(2 * np.pi * f_true * t + np.pi / 2) + 0.05 * np.random.randn(
        len(t)
    )

    f_nat = extract_natural_frequency(ax, ay, az, fs)
    print(f"Estimated natural frequency: {f_nat:.2f} Hz")