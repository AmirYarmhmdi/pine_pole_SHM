#Structural Health Monitoring for Wooden Poles

## Overview

This project implements two main approaches to estimate the **natural frequency** of wooden utility poles:

1. **Analytical estimation** based on the Euler–Bernoulli cantilever beam theory.
2. **Experimental estimation** from real 3-axis accelerometer data using FFT (Fast Fourier Transform).

The goal is to use frequency shifts as an indicator of structural health, helping detect decay or damage without destructive testing.

---

## 1️⃣ Analytical Natural Frequency Estimation

### Function

```python
def natural_frequency(L_free):
    ...
```

### Parameters

* `L_free`: Free length of the pole above ground [m].
* Returns: First natural frequency `[Hz]`.

### Methodology

The calculation is based on **Euler–Bernoulli beam theory** for a cantilever:

```
omega_n = beta_1**2 * sqrt(E*I / (m * L**4))
```

Where:

* `E` = Young’s modulus of wood (Pa)
* `I` = Moment of inertia of the cross-section [m^4]

  * For circular cross-section: `I = pi*d^4/64`
* `m` = Mass per unit length [kg/m]

  * For circular cross-section: `m = rho * pi * d^2 / 4`
* `L` = Free length above ground [m]
* `beta_1 = 1.875` (first-mode coefficient for a cantilever)
* `omega_n` = Angular frequency [rad/s]
* `f_n = omega_n / (2*pi)` = Frequency [Hz]

**Notes:**

* Diameter may vary along the height. The code samples the diameter along `L_free` and computes the **average diameter**.
* Guard clauses prevent division by zero for extremely small free lengths.

---

## 2️⃣ Experimental Natural Frequency Estimation from Accelerometer

### Function

```python
def extract_natural_frequency(ax, ay, az, fs, plot=True):
    ...
```

### Parameters

* `ax, ay, az`: Acceleration signals in X, Y, Z directions [m/s²]
* `fs`: Sampling frequency [Hz]
* `plot`: If `True`, plots time-domain and frequency-domain signals.

### Methodology

1. Compute the **magnitude of 3-axis acceleration**:

```
a_mag(t) = sqrt(ax^2 + ay^2 + az^2)
```

2. Remove DC offset to eliminate sensor bias:

```
a_mag(t) = a_mag(t) - mean(a_mag)
```

3. Compute **FFT** to obtain frequency spectrum:

```
A(f) = FFT(a_mag(t))
```

4. Identify the **dominant peak** (excluding 0 Hz) as the **natural frequency**.

5. Optional: Plot both the **time-domain acceleration magnitude** and **frequency spectrum** with the detected peak frequency highlighted.

### Notes

* High SNR is achieved when the sensor is placed at **~70–90% of the pole's free height**, where the mode shape of the first vibration mode has the highest amplitude.
* A single sensor is often sufficient per pole for the **first-mode frequency**, but multiple sensors can provide richer mode shape information for advanced structural analysis.

---

## 3️⃣ Material Assumptions

* Wood Type: Pine
* Young’s Modulus: `E = 11 GPa`
* Density: `ρ = 600 kg/m³`
* Cross-section: Circular, diameter varies along height

These assumptions are used for the analytical frequency estimation.

---

## 4️⃣ References

1. Chopra, A.K. *Dynamics of Structures*, 5th Edition, Pearson, 2017.
2. Doebling, S.W., Farrar, C.R., Prime, M.B., *A Summary Review of Vibration-Based Damage Identification Methods*, Shock and Vibration Digest, 1996.
3. ASTM D2899 – Standard Test Method for Vibration of Wood Poles (for field frequency measurement).
4. Ewins, D.J., *Modal Testing: Theory, Practice and Application*, 2000.

---

## 5️⃣ Usage

### Analytical Frequency

```python
f1 = natural_frequency(L_free=7.5)
print(f"Estimated natural frequency: {f1:.2f} Hz")
```

### Experimental Frequency from CSV

```python
ax, ay, az, fs = read_sensor_csv("sensor_data.csv")
f_nat = extract_natural_frequency(ax, ay, az, fs, plot=True)
print(f"Estimated natural frequency: {f_nat:.2f} Hz")
```

This approach enables **non-destructive evaluation** of wooden poles and can be integrated into **IoT-based monitoring systems**.

