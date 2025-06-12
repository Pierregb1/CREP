import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# === Données physiques ===
sigma = 5.67e-8      # Constante de Stefan-Boltzmann (W/m²·K⁴)
c = 551500           # Capacité thermique constante (J/K·m²)
h = 10               # Coefficient de convection (W/m²·K)
S0 = 1361            # Constan48te solaire (W/m²)
T_air = 283          # Température de l'air ambiant (K)
T0 = 283             # Température initiale (K)
dt = 3600            # Pas de temps : 1 heure

# === Dictionnaire d’albédo par région ===
data_albedo = {
    "Amérique du Nord": 0.25,
    "Amérique du Sud": 0.18,
    "Europe de l'Ouest": 0.25,
    "Europe de l'Est": 0.3,
    "Asie du Sud": 0.15,
    "Asie de l'Est": 0.2,
    "Asie du Sud-Est": 0.2,
    "Afrique du Nord": 0.25,
    "Afrique Sub-saharienne": 0.18,
    "Afrique_Désertique": 0.45,
    "Océans": 0.12,
    "Pole Nord": 0.75,
    "Pole Sud": 0.8
}

# === Fonctions ===
def determiner_partie_terre(latitude, longitude):
    if latitude >= 60: return "Pole Nord"
    elif latitude <= -60: return "Pole Sud"
    elif 30 <= latitude <= 60 and -130 <= longitude <= -60: return "Amérique du Nord"
    elif -60 <= latitude <= 15 and -90 <= longitude <= -30: return "Amérique du Sud"
    elif 45 <= latitude <= 70 and -10 <= longitude <= 40:
        return "Europe de l'Ouest" if longitude <= 20 else "Europe de l'Est"
    elif -10 <= latitude <= 40 and 60 <= longitude <= 160:
        if 5 <= latitude <= 30 and 60 <= longitude <= 120: return "Asie du Sud"
        elif 30 <= latitude <= 50 and 100 <= longitude <= 140: return "Asie de l'Est"
        else: return "Asie du Sud-Est"
    elif 15 <= latitude <= 30 and -20 <= longitude <= 40: return "Afrique_Désertique"
    elif -35 <= latitude <= 15 and -20 <= longitude <= 50:
        return "Afrique du Nord" if latitude > 0 else "Afrique Sub-saharienne"
    else: return "Océans"

def obtenir_albedo(lat, lon):
    return data_albedo[determiner_partie_terre(lat, lon)]

def puissance_recue_par_heure(latitude_deg, longitude_deg, jour_de_l_annee):
    lat = np.radians(latitude_deg)
    lon = np.radians(longitude_deg)
    inclinaison = np.radians(23.5)
    declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2 * np.pi * (jour_de_l_annee - 81) / 365))
    soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
    soleil /= np.linalg.norm(soleil)

    puissances = []
    for h in range(24):
        angle_terre = np.radians(15 * (h - 12))
        x = np.cos(lat) * np.cos(lon + angle_terre)
        y = np.cos(lat) * np.sin(lon + angle_terre)
        z = np.sin(lat)
        normale = np.array([x, y, z])
        prod = np.dot(normale, soleil)
        puissance = max(0, S0 * prod)
        puissances.append(puissance)
    return puissances

def temp_evolution(latitude, longitude, jour):
    P = puissance_recue_par_heure(latitude, longitude, jour)
    A = obtenir_albedo(latitude, longitude)
    T = [T0]
    for i in range(24):
        flux_entrant = (1 - A) * P[i]
        flux_sortant_rad = 0.5 * sigma * T[i]**4
        flux_convection = h * (T[i] - T_air)
        dT = dt * (flux_entrant - flux_sortant_rad - flux_convection) / c
        T.append(T[i] + dT)
    return T

# === Entrée utilisateur ===
latitude = float(input("Latitude (en degrés, ex: 48.85 pour Paris) : "))
longitude = float(input("Longitude (en degrés, ex: 2.35 pour Paris) : "))
jour = int(input("Jour de l'année (1-365) : "))

T_result = temp_evolution(latitude, longitude, jour)

# === Affichage sur carte ===
fig = plt.figure(figsize=(12, 6))

# Carte avec le point localisé
plt.subplot(1, 2, 1)
m = Basemap(projection='robin', lon_0=0, resolution='c')
m.drawcoastlines()
m.drawcountries()
x, y = m(longitude, latitude)
m.plot(x, y, 'ro', markersize=8)
plt.title(f"Localisation : lat={latitude}, lon={longitude}")

# Température
plt.subplot(1, 2, 2)
plt.plot(range(25), np.array(T_result) - 273.15, color='orange')
plt.xlabel("Heure (UTC)")
plt.ylabel("Température (°C)")
plt.title(f"Évolution de la température sur 24h (jour {jour})")
plt.grid()

plt.tight_layout()
plt.show()

