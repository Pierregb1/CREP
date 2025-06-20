
import math

def puissance_sol(lat, lon, jour):
    S0 = 1361
    lat = math.radians(lat)
    lon = math.radians(lon)
    inclinaison = math.radians(23.5)
    declinaison = math.asin(math.sin(inclinaison) * math.sin(2 * math.pi * (jour - 81) / 365))
    soleil = [math.cos(declinaison), 0, math.sin(declinaison)]
    norme = math.sqrt(sum(s**2 for s in soleil))
    soleil = [s / norme for s in soleil]
    puissances = []
    for h in range(24):
        angle = math.radians(15 * (h - 12))
        x = math.cos(lat) * math.cos(lon + angle)
        y = math.cos(lat) * math.sin(lon + angle)
        z = math.sin(lat)
        normale = [x, y, z]
        dot = sum(n * s for n, s in zip(normale, soleil))
        puissances.append(max(0, S0 * dot))
    return puissances

def temp(lat, lon):
    P = [puissance_sol(lat, lon, j) for j in range(1, 366)]
    P = [p for jour in P for p in jour]  # aplatir
    T = [273]
    c = 1.5e5
    S = 1
    sigma = 5.67e-8
    A = 0.3
    dt = 3600
    for i in range(len(P)):
        flux_sortant = sigma * S * T[-1]**4
        T.append(T[-1] + dt * ((1 - A) * P[i] - flux_sortant) / c)
    return T
