# MODULES À INSTALLER (si nécessaire) :
# pip install numpy matplotlib basemap

import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# ------------------------------------------------------------
# Constantes
# ------------------------------------------------------------
S = 1361  # Constante solaire à la distance de la Terre (W/m²)
omega = 2 * math.pi / 24  # Vitesse de rotation terrestre (rad/h)

# Inclinaison de la Terre (20°)
epsilon_deg = 20
epsilon_rad = math.radians(epsilon_deg)
cos_eps = math.cos(epsilon_rad)
sin_eps = math.sin(epsilon_rad)

# ------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------
def geodetic_to_spherical(lat_deg, lon_deg):
    """
    Convertit latitude (°N) et longitude (°E) en colatitude θ et longitude φ (en rad).
    """
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)
    theta = np.pi / 2 - lat   # colatitude
    phi = lon                 # longitude
    return theta, phi

def inclined_normal_vector(theta, phi):
    """
    Vecteur normal incliné après rotation autour de l'axe X de 20°.
    """
    nx = math.sin(theta) * math.cos(phi)
    ny = cos_eps * math.sin(theta) * math.sin(phi) - sin_eps * math.cos(theta)
    nz = sin_eps * math.sin(theta) * math.sin(phi) + cos_eps * math.cos(theta)
    return np.array([nx, ny, nz])

def solar_direction(t):
    """
    Vecteur direction du Soleil dans le repère non incliné.
    """
    sx = -math.sin(omega * t)
    sy = -math.cos(omega * t)
    sz = 0.0
    return np.array([sx, sy, sz])

def inclined_power_density(lat_deg, lon_deg, t_hour):
    """
    Calcule la puissance reçue en tenant compte de l'inclinaison de la Terre.
    """
    theta, phi = geodetic_to_spherical(lat_deg, lon_deg)
    n = inclined_normal_vector(theta, phi)
    s0 = solar_direction(t_hour)
    dot_ns = np.dot(n, s0)
    return S * (-dot_ns) if dot_ns < 0 else 0.0

def read_float(prompt, min_val=None, max_val=None):
    while True:
        s = input(prompt).strip()
        try:
            val = float(s)
        except ValueError:
            print("➜ Entrée non valide : veuillez saisir un nombre.")
            continue
        if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
            print(f"➜ La valeur doit être comprise entre {min_val} et {max_val}.")
            continue
        return val

def read_time_hhmm(prompt):
    while True:
        s = input(prompt).strip()
        if ':' not in s:
            print("➜ Format invalide. Utilisez HH:MM.")
            continue
        hh_str, mm_str = s.split(':')
        if not (hh_str.isdigit() and mm_str.isdigit()):
            print("➜ Heures et minutes doivent être des entiers.")
            continue
        hh = int(hh_str)
        mm = int(mm_str)
        if hh < 0 or hh > 23 or mm < 0 or mm > 59:
            print("➜ Heures : 0–23, Minutes : 0–59.")
            continue
        return hh + mm / 60.0

# ------------------------------------------------------------
# Programme principal
# ------------------------------------------------------------
if __name__ == "__main__":
    try:
        lat = read_float("Entrer la latitude (−90 à +90) : ", min_val=-90.0, max_val=90.0)
        lon = read_float("Entrer la longitude (−180 à +180) : ", min_val=-180.0, max_val=180.0)
        t_utc = read_time_hhmm("Entrer l'heure UTC (format HH:MM) : ")

        times24 = np.linspace(0, 24, 500)
        real_times = (times24 + t_utc) % 24

        power_values = [inclined_power_density(lat, lon, hr) for hr in real_times]
        power_values = np.array(power_values)

        # Affichage du graphique
        plt.figure(figsize=(10, 5))
        plt.plot(times24, power_values, color='darkorange', lw=2,
                 label=f"Point ({lat:.2f}°, {lon:.2f}°)")
        plt.axvline((12 - t_utc) % 24, color='gray', linestyle='--',
                    label="Midi local (approx.)")
        plt.title("Puissance solaire reçue sur 24 h (avec inclinaison de 20°)")
        plt.xlabel("Heure locale (heures décimales)")
        plt.ylabel("Puissance reçue (W/m²)")
        plt.xlim(0, 24)
        plt.xticks(np.arange(0, 25, 2))
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Carte géographique
        fig, ax = plt.subplots(figsize=(8, 6))
        m = Basemap(projection='ortho', lat_0=lat, lon_0=lon, resolution='l', ax=ax)
        m.drawcoastlines()
        m.drawcountries()
        m.fillcontinents(color='lightgray', lake_color='aqua')
        m.drawmapboundary(fill_color='aqua')

        xpt, ypt = m(lon, lat)
        m.plot(xpt, ypt, 'ro', markersize=8)
        plt.title(f"Position géographique ({lat:.2f}°, {lon:.2f}°)")
        plt.show()

    except Exception as exc:
        print(f"Erreur inattendue : {exc}")
