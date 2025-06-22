
import numpy as np
import math

def temp(lat, lon):
    c = 1.5e5
    sigma = 5.67e-8
    A = 0.3
    dt = 3600
    S = 1
    S0 = 1361
    T = [273]
    for j in range(365):
        declinaison = np.arcsin(np.sin(math.radians(23.5)) * np.sin(2 * math.pi * (j - 81) / 365))
        soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
        soleil /= np.linalg.norm(soleil)
        for h in range(24):
            angle = math.radians(15 * (h - 12))
            x = np.cos(math.radians(lat)) * np.cos(math.radians(lon) + angle)
            y = np.cos(math.radians(lat)) * np.sin(math.radians(lon) + angle)
            z = np.sin(math.radians(lat))
            normale = np.array([x, y, z])
            P = max(0, S0 * np.dot(normale, soleil))
            flux_sortant = sigma * S * T[-1]**4
            T.append(T[-1] + dt * ((1 - A) * P - flux_sortant) / c)
    return T
