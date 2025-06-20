
import requests
import numpy as np

def get_data(lat, lon):
    url = f"https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=ALLSKY_SFC_SW_DWN,WS10M&community=RE&longitude={lon}&latitude={lat}&format=JSON&start=2024&end=2024"
    r = requests.get(url)
    data = r.json()
    P = list(data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"].values())
    V = list(data["properties"]["parameter"]["WS10M"].values())
    return P, V

def temp(lat, lon):
    P, V = get_data(lat, lon)
    T = [273]
    c = 1.5e5
    sigma = 5.67e-8
    A = 0.3
    dt = 3600
    S = 1
    for i in range(len(P)):
        flux_sortant = sigma * S * T[-1]**4
        T.append(T[-1] + dt * ((1 - A) * P[i] - flux_sortant) / c)
    return T
