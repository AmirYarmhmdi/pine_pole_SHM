# utils/pole_est.py
# ===========================

import json
import os

import numpy as np


def load_config():
    config_path = os.path.join("config", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)


config = load_config()
mat = config["material"]
cable = config["cable"]

E = mat["E_GPa"] * 1e9
rho = mat["density"]

CABLE_MASS_PER_M = cable["linear_mass"]
CABLE_LENGTH_EFFECTIVE = cable["effective_length"]
ATTACH_OFFSET_FROM_TOP = cable["attachment_offset"]
CABLE_TOTAL_MASS = CABLE_MASS_PER_M * CABLE_LENGTH_EFFECTIVE

heights = np.array([0.0, 7.5, 9.0])
diameters = np.array([0.170, 0.210, 0.249375])


def pole_diameter(h):
    return np.interp(h, heights, diameters)


def height_from_diameter(d):
    return np.interp(d, diameters, heights)


def height_from_circumference(C):
    d = C / np.pi
    return height_from_diameter(d)


def phi_cantilever_mode1(x, L):
    if L <= 0:
        return 0.0
    beta = 1.875
    xi = x / L
    c, s = np.cosh(beta * xi), np.sinh(beta * xi)
    co, si = np.cos(beta * xi), np.sin(beta * xi)
    denom = np.sinh(beta) + np.sin(beta)
    alpha = (np.cosh(beta) + np.cos(beta)) / denom
    phi = c - co - alpha * (s - si)
    phi_L = np.cosh(beta) - np.cos(beta) - alpha * (np.sinh(beta) - np.sin(beta))
    return phi / phi_L


def natural_frequency(L_free):
    if L_free <= 0.0:
        return np.nan

    h_samples = np.linspace(0, L_free, 100)
    d_avg = np.mean(pole_diameter(h_samples))

    I = (np.pi / 64) * d_avg**4
    m_line = rho * (np.pi / 4) * d_avg**2
    k_eq = 3 * E * I / (L_free**3)
    m_eff = 0.23 * m_line * L_free

    x_attach = max(L_free - ATTACH_OFFSET_FROM_TOP, 0.0)
    phi = phi_cantilever_mode1(x_attach, L_free)
    M_att_eff = CABLE_TOTAL_MASS * (phi**2)

    omega_n = np.sqrt(k_eq / (m_eff + M_att_eff))
    return omega_n / (2 * np.pi)


def print_material_assumptions():
    print("\n=== Material Assumptions (Pine Wood) ===")
    print(f"Young's Modulus (E): {mat['E_GPa']:.2f} GPa")
    print(f"Density (ρ): {mat['density']} kg/m³")
    print(f"Model: {mat['model']}")
    print(f"Assumes: {mat['assumptions']}")
    print("\n=== Cable / Messenger Assumptions ===")
    print(f"Cable type: {cable['type']}")
    print(f"Linear mass: {CABLE_MASS_PER_M:.3f} kg/m")
    print(f"Effective coupled length: {CABLE_LENGTH_EFFECTIVE:.2f} m")
    print(f"Total attached mass: {CABLE_TOTAL_MASS:.2f} kg")
    print(f"Attachment point: {ATTACH_OFFSET_FROM_TOP:.2f} m below the tip")
