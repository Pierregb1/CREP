import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# === Données physiques ===
sigma = 5.67e-8      # Constante de Stefan-Boltzmann (W/m²·K⁴)
c = 551500           # Capacité thermique constante (J/K·m²)
h = 10               # Coefficient de convection (W/m²·K)
S0 = 1361            # Constante solaire (W/m²)
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
        flux_sortant = sigma * T[-1]**4 + h * (T[-1] - T_air)
        delta_T = dt * (flux_entrant - flux_sortant) / c
        T.append(T[-1] + delta_T)
    return T[1:]

# === Partie interaction carte ===
def calculer_temperature_horaire_sur_an(lat, lon):
    temperatures = []
    for jour in range(1, 366):
        T_heure = temp_evolution(lat, lon, jour)  # liste de 24 valeurs
        temperatures.extend(T_heure)  # ajouter les 24 heures du jour
    return temperatures

def tracer_temperature_horaire_sur_an(lat, lon):
    temperatures = calculer_temperature_horaire_sur_an(lat, lon)
    heures = np.arange(1, len(temperatures) + 1)
    plt.figure(figsize=(14, 5))
    plt.plot(heures, temperatures, linewidth=0.8)
    plt.xlabel("Heure de l'année")
    plt.ylabel("Température (K)")
    plt.title(f"Évolution de la température horaire pendant un an\nLat: {lat:.2f}, Lon: {lon:.2f}")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def on_click(event, m):
    if event.xdata is None or event.ydata is None:
        return
    lon, lat = m(event.xdata, event.ydata, inverse=True)
    print(f"Point sélectionné : latitude = {lat:.2f}, longitude = {lon:.2f}")
    tracer_temperature_horaire_sur_an(lat, lon)

def afficher_carte_et_interagir():
    fig, ax = plt.subplots(figsize=(12, 6))
    m = Basemap(projection='mill', resolution='c', ax=ax)
    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary()
    plt.title("Cliquez sur un point pour afficher la température horaire sur un an")
    fig.canvas.mpl_connect('button_press_event', lambda event: on_click(event, m))
    plt.show()

if __name__ == "__main__":
    afficher_carte_et_interagir()
