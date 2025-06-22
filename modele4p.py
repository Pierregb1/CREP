
import requests

def get_data(lat, lon):
    url = f"https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=ALLSKY_SFC_SW_DWN,WS10M&community=RE&longitude={lon}&latitude={lat}&format=JSON&start=2024&end=2024"
    r = requests.get(url)
    data = r.json()
    P = list(data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"].values())
    V = list(data["properties"]["parameter"]["WS10M"].values())
    P = [v if v is not None else 0 for v in P]
    V = [v if v is not None else 0 for v in V]
    # Clamp des puissances pour éviter des valeurs irréalistes
    P = [min(max(p, 0), 1500) for p in P]
    return P, V

def temp(lat, lon):
    P, V = get_data(lat, lon)
    T = [273]
    c = 1.5e5
    sigma = 5.67e-8
    A = 0.3
    dt = 3600
    S = 1
    MAX_TEMP = 373  # Clamp température max à 100°C
    for i in range(len(P)):
        T_last = min(T[-1], MAX_TEMP)
        flux_sortant = sigma * S * T_last**4
        T.append(T_last + dt * ((1 - A) * P[i] - flux_sortant) / c)
    return T
