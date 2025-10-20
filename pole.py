import numpy as np

# ---- Geometric reference data ----
# Heights are measured from the pole top (0 m) downwards
heights = np.array([0.0, 7.5, 9.0])  # [m]
diameters = np.array([0.170, 0.210, 0.249375])  # [m]

# ---- Material properties for pine wood (assumed) ----
E = 11e9  # Young's modulus [Pa]
rho = 600  # Density [kg/m3]
g = 9.81  # Gravity [m/s2], not directly used but kept for completeness


def pole_diameter(h):
    """Interpolate the pole diameter [m] at a given height h [m]."""
    return np.interp(h, heights, diameters)


def height_from_diameter(d):
    """
    Inverse relation: estimate the height [m] from a given diameter [m].
    NOTE: np.interp requires that 'diameters' be sorted in ascending order.
    """
    # Ensure diameter array is strictly increasing for interp
    # (here diameters is already increasing, so direct interp is correct)
    return np.interp(d, diameters, heights)


def natural_frequency(L_free):
    """
    Estimate the first natural frequency (Hz) of the wooden pole
    using the Euler–Bernoulli cantilever beam theory.

    Parameters:
        L_free (float): Free length of the pole above ground [m].
    Returns:
        f_n (float): First natural frequency [Hz] (or np.nan if not computable).
    """
    # guard against zero or extremely small free length (singularity)
    if L_free <= 0.0:
        return np.nan

    # Sample diameter distribution along the free part
    h_samples = np.linspace(0, L_free, 100)
    d_samples = pole_diameter(h_samples)
    d_avg = np.mean(d_samples)

    # Moment of inertia and mass per unit length (circular section)
    I = (np.pi / 64) * d_avg**4
    m = rho * (np.pi / 4) * d_avg**2

    # First mode coefficient for a cantilever
    beta1 = 1.875
    # Avoid unexpected zero division if L_free is extremely small
    if L_free**4 <= 1e-12:
        return np.nan

    omega_n = (beta1**2) * np.sqrt(E * I / (m * L_free**4))  # [rad/s]
    f_n = omega_n / (2 * np.pi)  # [Hz]
    return f_n


def print_material_assumptions():
    """Display the assumed material properties for transparency."""
    print("\n=== Material Assumptions (Pine Wood) ===")
    print(f"Young's Modulus (E): {E/1e9:.2f} GPa")
    print(f"Density (ρ): {rho} kg/m³")
    print(f"Model: Euler–Bernoulli Cantilever Beam (Fixed at Ground)")
    print("Assumes uniform material and small vibration amplitude.\n")


def main():
    print("=== Natural Frequency Estimator for Wooden Utility Poles ===")
    print("1️⃣ Option 1: Enter height above ground (m)")
    print("2️⃣ Option 2: Enter pole diameter at ground surface (m)\n")

    mode = input("Select an option (1 or 2): ").strip()

    if mode == "1":
        try:
            L_free = float(input("Enter height above ground (m): ").strip())
        except ValueError:
            print("❌ Invalid numeric value.")
            return
        if not 0 < L_free < 9:
            print("❌ Height must be > 0 and < 9 meters.")
            return
        L_buried = 9 - L_free
        f1 = natural_frequency(L_free)

        print_material_assumptions()
        print(f"📏 Buried length: {L_buried:.2f} m")
        if np.isnan(f1):
            print("⚠️ First natural frequency: Not computable for given geometry.")
        else:
            print(f"🎵 First natural frequency: {f1:.2f} Hz")

    elif mode == "2":
        try:
            d_ground = float(input("Enter pole diameter at ground level (m): ").strip())
        except ValueError:
            print("❌ Invalid numeric value.")
            return
        # check diameter bounds
        d_min = diameters.min()
        d_max = diameters.max()
        if not (d_min <= d_ground <= d_max):
            print(f"❌ Diameter is out of valid range [{d_min:.3f} m - {d_max:.6f} m].")
            return

        # Determine the height corresponding to this diameter
        h_ground = height_from_diameter(d_ground)
        L_free = h_ground
        if not 0 < L_free < 9:
            print("❌ Computed height is out of physical bounds.")
            return

        L_buried = 9 - L_free
        f1 = natural_frequency(L_free)

        print_material_assumptions()
        print(f"📏 Height above ground: {L_free:.2f} m")
        print(f"📥 Buried length: {L_buried:.2f} m")
        if np.isnan(f1):
            print("⚠️ First natural frequency: Not computable for given geometry.")
        else:
            print(f"🎵 First natural frequency: {f1:.2f} Hz")

    else:
        print("❌ Invalid selection. Please choose 1 or 2.")


if __name__ == "__main__":
    main()
