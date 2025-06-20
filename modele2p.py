
import math
import numpy as np

def puissance(lat, lon, jour):
    S0 = 1361
    lat = math.radians(lat)
    lon = math.radians(lon)
    inclinaison = math.radians(23.5)
    declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2 * math.pi * (jour - 81) / 365))
    soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
    soleil /= np.linalg.norm(soleil)
    puissances = []
    for h in range(24):
        angle = math.radians(15 * (h - 12))
        x = np.cos(lat) * np.cos(lon + angle)
        y = np.cos(lat) * np.sin(lon + angle)
        z = np.sin(lat)
        normale = np.array([x, y, z])
        puissances.append(max(0, S0 * np.dot(normale, soleil)))
    return puissances

def chaque_jour(lat, lon):
    return [puissance(lat, lon, j) for j in range(1, 366)]

def annee(P):
    return [val for jour in P for val in jour]

def temp(lat, lon):
    P_recu = annee(chaque_jour(lat, lon))
    c = 1.5e5
    S = 1
    T0 = 273
    sigma = 5.67e-8
    dt = 3600
    A = 0.3
    T = [T0]
    for i in range(len(P_recu)):
        flux_sortant = 0.5 * sigma * S * (T[i])**4
        T.append(T[i] + dt * ((1 - A) * P_recu[i] * S - flux_sortant) / c)
    return T
