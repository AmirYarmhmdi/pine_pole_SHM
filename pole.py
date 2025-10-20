import numpy as np

# ---- Known geometric data (in meters) ----
# total length = 9.0 m, 1.5 m below ground, 7.5 m above
heights = np.array([0.0, 7.5, 9.0])  # from top (0) to bottom (9)
diameters = np.array([0.170, 0.210, 0.249375])  # in meters

# ---- Material properties for wood (approximate) ----
E = 11e9  # Young's modulus [Pa] for pine wood
rho = 600  # density [kg/m3]
g = 9.81


def pole_diameter(h):
    """Linear interpolation of diameter [m] given height from top."""
    return np.interp(h, heights, diameters)


def natural_frequency(L_free):
    """
    Estimate the first natural frequency (Hz) of a cantilever pole.
    L_free: length above ground (m)
    """
    # Effective pole length (above ground only)
    L = L_free

    # Compute average diameter along free part
    h_samples = np.linspace(0, L, 100)
    d_samples = pole_diameter(h_samples)
    d_avg = np.mean(d_samples)

    # Moment of inertia and mass per unit length
    I = (np.pi / 64) * d_avg**4
    m = rho * (np.pi / 4) * d_avg**2

    # Fundamental frequency for cantilever (Euler–Bernoulli)
    beta1 = 1.875  # first mode constant
    omega_n = (beta1**2) * np.sqrt(E * I / (m * L**4))  # rad/s
    f_n = omega_n / (2 * np.pi)  # Hz

    return f_n


if __name__ == "__main__":
    print("=== Natural Frequency Estimator for Wooden Poles ===")
    print("Assumptions:pole tottal length = 9.0 \nE = 11e9 [Pa] for pine wood \n      rho = 600  # density [kg/m3] \n     g = 9.81")
    L_total = 9.0  # total pole length (m)

    L_free = float(input("Enter height above ground (m): "))
    if L_free >= L_total:
        print("Invalid: height above ground exceeds total pole length.")
    else:
        L_buried = L_total - L_free
        f1 = natural_frequency(L_free)
        print(f"\nBuried length: {L_buried:.2f} m")
        print(f"Estimated first natural frequency: {f1:.2f} Hz")
