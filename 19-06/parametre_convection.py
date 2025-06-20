# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 15:10:53 2025

@author: jeann
"""
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

def liste_h (lat,long):
    L = []
    v = get_daily_wind_speed(lat, long)
    for i in range(365):
        for j in range (24):
            L.append(coefficient_convection(v[i]))
    return(L)