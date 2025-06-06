# MODULES À INSTALLER (si nécessaire) :
# pip install numpy matplotlib basemap

import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# ------------------------------------------------------------
# Constantes
# ------------------------------------------------------------
S = 1361            # Constante solaire à la distance de la Terre (W/m²)
omega = 2 * math.pi / 24   # Vitesse de rotation terrestre (rad/h)

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

def normal_vector(theta, phi):
    """
    Renvoie le vecteur normal unitaire (non incliné) à la surface terrestre,
    en coordonnées sphériques (colatitude θ, longitude φ).
    """
    nx = math.sin(theta) * math.cos(phi)
    ny = math.sin(theta) * math.sin(phi)
    nz = math.cos(theta)
    return np.array([nx, ny, nz])

def solar_direction(t):
    """
    Vecteur direction du Soleil, dans le repère terrestre non incliné,
    en fonction du temps t (en heures décimales).
    
    s0(t) = ( -sin(ω t),  -cos(ω t),  0 )
    """
    sx = -math.sin(omega * t)
    sy = -math.cos(omega * t)
    sz = 0.0
    return np.array([sx, sy, sz])

def instantaneous_power_density(lat_deg, lon_deg, t_hour):
    """
    Calcule la puissance solaire reçue (W/m²) en un point de coordonnées
    (latitude, longitude) à l’heure t_hour (en heures décimales UTC).
    On suppose la Terre non inclinée pour ce calcul.
    """
    # 1) Conversion en colatitude et longitude (rad)
    theta, phi = geodetic_to_spherical(lat_deg, lon_deg)
    # 2) Vecteur normal local
    n = normal_vector(theta, phi)
    # 3) Vecteur Soleil au temps t
    s0 = solar_direction(t_hour)
    # 4) Produit scalaire
    dot_ns = np.dot(n, s0)
    if dot_ns < 0:
        return S * (-dot_ns)
    else:
        return 0.0

def read_float(prompt, min_val=None, max_val=None):
    """
    Demande un float à l'utilisateur jusqu'à obtenir une valeur valide.
    Si min_val/max_val sont spécifiés, la valeur lue doit être dans [min_val, max_val].
    """
    while True:
        s = input(prompt).strip()
        try:
            val = float(s)
        except ValueError:
            print("➜ Entrée non valide : veuillez saisir un nombre (en notation décimale).")
            continue
        if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
            print(f"➜ La valeur doit être comprise entre {min_val} et {max_val}.")
            continue
        return val

def read_time_hhmm(prompt):
    """
    Demande un horaire au format HH:MM (00 ≤ HH ≤ 23, 00 ≤ MM ≤ 59) 
    et renvoie l'heure en dizaineur (ex. "13:30" → 13.5).
    """
    while True:
        s = input(prompt).strip()
        if ':' not in s:
            print("➜ Format invalide. Veuillez utiliser HH:MM (ex : 07:45).")
            continue
        parts = s.split(':')
        if len(parts) != 2:
            print("➜ Format invalide. Veuillez utiliser HH:MM.")
            continue
        hh_str, mm_str = parts
        if not (hh_str.isdigit() and mm_str.isdigit()):
            print("➜ Heures et minutes doivent être des nombres entiers.")
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
        # Lecture sécurisée de la latitude et de la longitude
        lat = read_float("Entrer la latitude (−90 à +90) : ", min_val=-90.0, max_val=90.0)
        lon = read_float("Entrer la longitude (−180 à +180) : ", min_val=-180.0, max_val=180.0)
        
        # Lecture sécurisée de l’heure en format HH:MM
        t_utc = read_time_hhmm("Entrer l'heure UTC (format HH:MM) : ")
        
        # On veut visualiser la puissance sur 24h ; on décale ensuite en fonction de t_utc
        # (par exemple, si t_utc = 06:30, cela signifie que l'instant '0' correspond à 06h30 UTC).
        # On construit un vecteur de 24h pondéré par un pas de 500 points.
        times24 = np.linspace(0, 24, 500)
        
        # Pour chaque instant u dans [0,24], on veut connaître l'heure réelle = (u + t_utc) mod 24
        real_times = (times24 + t_utc) % 24
        
        # Calcul des puissances reçues à chaque instant réel
        power_values = [instantaneous_power_density(lat, lon, hr) for hr in real_times]
        power_values = np.array(power_values)
        
        # --- Affichage du graphique puissance vs temps ---
        plt.figure(figsize=(10, 5))
        plt.plot(times24, power_values, color='darkorange', lw=2,
                 label=f"Point ({lat:.2f}°, {lon:.2f}°)")
        plt.axvline((12 - t_utc) % 24, color='gray', linestyle='--',
                    label="Midi local (approx.)")
        plt.title("Puissance solaire reçue sur 24 h (point fixe)")
        plt.xlabel("Heure locale (heures décimales)")
        plt.ylabel("Puissance reçue (W/m²)")
        plt.xlim(0, 24)
        plt.xticks(np.arange(0, 25, 2))
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
        # --- Affichage d’une carte orthographique avec le point marqué ---
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
