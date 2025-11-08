# ============================================================
# utils/pole_est.py
# Analytical Natural Frequency Estimator for Wooden Utility Poles
# Supports: Free-standing poles & poles with lateral support
# ============================================================

import json
import os

import numpy as np

from utils.config_loader import load_config

# ============================================================
# 1️⃣ Load configuration
# ============================================================
CONFIG = load_config()
mat = CONFIG["material"]
cable = CONFIG["cable"]

# ============================================================
# 2️⃣ Material & Cable Parameters
# ============================================================

E = mat["E_GPa"] * 1e9  # [Pa]
rho = mat["density"]  # [kg/m³]
E_name = mat.get("species", "Pine Wood")

CABLE_MASS_PER_M = cable["linear_mass"]  # [kg/m]
CABLE_LENGTH_EFFECTIVE = cable["effective_length"]  # [m]
ATTACH_OFFSET_FROM_TOP = cable["attachment_offset"]  # [m]
CABLE_TOTAL_MASS = CABLE_MASS_PER_M * CABLE_LENGTH_EFFECTIVE  # [kg]

# ============================================================
# 3️⃣ Geometric Reference Data (measured)
# ============================================================

# Height from top downwards [m]
heights = np.array([0.0, 7.5, 9.0])
# Corresponding diameters [m]
diameters = np.array([0.170, 0.210, 0.249375])

# ============================================================
# 4️⃣ Helper Functions
# ============================================================


def pole_diameter(h):
    """Interpolate pole diameter [m] at height h [m] from top."""
    return np.interp(h, heights, diameters)


def height_from_diameter(d):
    """Inverse interpolation: estimate height from diameter."""
    return np.interp(d, diameters, heights)


def height_from_circumference(C):
    """Estimate height from measured circumference [m]."""
    d = C / np.pi
    return height_from_diameter(d)


# ============================================================
# 5️⃣ Mode Shape & Analytical Frequency (Free Pole)
# ============================================================


def natural_frequency(L_free):
    """
    Estimate the first natural frequency (Hz) of the wooden pole
    using Euler-Bernoulli cantilever beam theory.
    """
    if L_free <= 0.0:
        return np.nan

    # Sample geometry
    h_samples = np.linspace(0, L_free, 100)
    d_samples = pole_diameter(h_samples)
    d_avg = np.mean(d_samples)

    # Section properties
    I = (np.pi / 64) * d_avg**4
    m = rho * (np.pi / 4) * d_avg**2

    # Fundamental frequency (cantilever)
    beta1 = 1.875
    omega_n = (beta1**2) * np.sqrt(E * I / (m * L_free**4))
    f_n = omega_n / (2 * np.pi)

    # Include effect of attached cable mass
    if CABLE_TOTAL_MASS > 0:
        M_eff = 0.23 * m * L_free  # effective mass of beam (mode 1)
        phi = 1.0  # assume attached near tip
        f_n = f_n * np.sqrt(M_eff / (M_eff + CABLE_TOTAL_MASS * phi**2))

    return f_n


# ============================================================
# 6️⃣ Analytical Frequency (Pole with Lateral Support)
# ============================================================


def natural_frequency_with_support(L_free, h_support):
    """
    Estimate first natural frequency (Hz) for a pole with a lateral support.
    Support typically a 45° wooden brace attached at height h_support (m).
    Uses empirical stiffness amplification factor:
        f_supported = f_free * (1 + 0.3 * (h_support / L_free))
    """
    if L_free <= 0.0:
        return np.nan

    f_free = natural_frequency(L_free)
    if np.isnan(f_free):
        return np.nan

    # Normalize support height ratio (avoid over/under scaling)
    ratio = np.clip(h_support / L_free, 0.1, 0.9)
    stiff_factor = 1.0 + 0.3 * ratio
    f_supported = f_free * stiff_factor
    return f_supported


# ============================================================
# 7️⃣ Display Material and Cable Info
# ============================================================


def print_material_assumptions():
    """Display material and cable assumptions loaded from config."""
    print("\n=== Material Assumptions ===")
    print(f"Wood Species: {E_name}")
    print(f"Young's Modulus (E): {E/1e9:.2f} GPa")
    print(f"Density (ρ): {rho:.1f} kg/m³")
    print(f"Model: {mat['model']}")
    print(f"Assumptions: {mat['assumptions']}")

    print("\n=== Cable / Messenger Assumptions ===")
    print(f"Type: {cable['type']}")
    print(f"Linear mass: {CABLE_MASS_PER_M:.3f} kg/m")
    print(f"Effective coupled length: {CABLE_LENGTH_EFFECTIVE:.2f} m")
    print(f"Total attached mass: {CABLE_TOTAL_MASS:.2f} kg")
    print(f"Attachment point: {ATTACH_OFFSET_FROM_TOP:.2f} m below tip\n")
