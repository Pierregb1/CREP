# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 14:18:02 2025

@author: jeann
"""


import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import requests

# ---------------------- Convection par vitesse de vent ---------------------- #
def coefficient_convection(v):
    rho = 1.2         # Masse volumique de l'air (kg/m³)
    mu = 1.8e-5       # Viscosité dynamique de l'air (Pa·s)
    L = 1.0           # Longueur caractéristique (m)
    Pr = 0.71         # Nombre de Prandtl pour l'air
    lambda_air = 0.026  # Conductivité thermique de l'air (W/m·K)

    Re = rho * v * L / mu
    if Re < 5e5:
        C, m, n = 0.664, 0.5, 1/3
    else:
        C, m, n = 0.037, 0.8, 1/3

    Nu = C * Re**m * Pr**n
    h = Nu * lambda_air / L
    return h

# ---------------------- API Nasa pour le vent ---------------------- #
def get_daily_wind_speed(lat, lon, start="20240101", end="20241231"):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "WS2M",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        wind_data = data["properties"]["parameter"]["WS2M"]
        wind_values = [wind_data[day] for day in sorted(wind_data)]
        return wind_values  # Liste de 365 vitesses moyennes journalières
    except Exception as e:
        print("Erreur lors de la récupération du vent :", e)
        return [2.5] * 365  # Valeur par défaut


# ---------------------- API NASA POWER pour l’albédo ---------------------- #
def get_mean_albedo(lat, lon, start="20220101", end="20231231"):
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        allsky = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        upsky = data['properties']['parameter']['ALLSKY_SFC_SW_UP']

        albedo_values = [
            upsky[day] / allsky[day]
            for day in allsky if allsky[day] > 0 and upsky[day] is not None
        ]
        return sum(albedo_values) / len(albedo_values) if albedo_values else 0.3
    except Exception as e:
        print("Erreur lors de la récupération de l'albédo :", e)
        return 0.3

# ---------------------- Simulation Température ---------------------- #
def temp(P_recu, vitesses_vent_journalières, A):
    c = 2.25e5
    S = 1
    T0 = 283
    sigma = 5.67e-8
    dt = 3600
    T_air = 283
    T = [T0]

    for i in range(len(P_recu)):
        jour = i // 24
        v = vitesses_vent_journalières[jour]
        h = coefficient_convection(v)
        flux_entrant = (1 - A) * P_recu[i] * S
        flux_sortant_rad = 0.5 * sigma * S * T[i]**4
        flux_convection = h * S * (T[i] - T_air)
        dT = dt * (flux_entrant - flux_sortant_rad - flux_convection) / c
        T.append(T[i] + dT)
    return T

# ---------------------- Modèle Solaire ---------------------- #
def puissance_recue_par_heure(latitude_deg, longitude_deg, jour_de_l_annee):
    S0 = 1361
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
        puissances.append(max(0, S0 * prod))
    return puissances

def chaque_jour(lat, lon):
    return [puissance_recue_par_heure(lat, lon, j) for j in range(1, 366)]

def annee(P_tout):
    return [val for jour in P_tout for val in jour]

# ---------------------- Paramètres du point d’étude ---------------------- #
lat, lon = 28.85, 2.35  # Paris
P_annuelle = annee(chaque_jour(lat, lon))
vent_journalier = get_daily_wind_speed(lat, lon)
A = get_mean_albedo(lat, lon)

# Simulation température
T_point = temp(P_annuelle, vent_journalier, A)

# ---------------------- Affichage ---------------------- #
date_debut = datetime.datetime(2024, 1, 1)
dates = [date_debut + datetime.timedelta(hours=i) for i in range(len(T_point))]

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(dates, T_point)

locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)

ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)

plt.xlabel("Date")
plt.ylabel("Température (K)")
plt.title(f"Température simulée à Paris ({lat}°N, {lon}°E) en 2024")
plt.grid(True)
plt.tight_layout()
plt.show()
