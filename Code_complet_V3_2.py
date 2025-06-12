import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import requests

# Coordonnées Paris
lat, lon = 48.85, 2.35

def get_mean_albedo(lat, lon, start="20220101", end="20231231"):
    """
    Renvoie l'albédo moyen sur la période donnée pour un point donné (lat, lon).
    start, end : dates au format 'YYYYMMDD'
    """
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
        return sum(albedo_values) / len(albedo_values) if albedo_values else None

    except Exception as e:
        print("Erreur lors de la récupération de l'albédo :", e)
        return None

start_date1 = "20220101"
end_date1 = "20231231"

def temp(P_recu):

    """
    renvoie une liste de température à partir d'une liste de puissance recue
    entrée: Liste de puissances reçues au cours du temps
    sortie: Liste de températures évaluées en fonction du temps

    """

    c = 2.25e5        # Capacité thermique (J/K) pour 0.1 m de sol humide
    alpha = 0           # Coefficient effet de serre (inutile ici)
    S = 1               # Surface (m²)
    T0 = 283            # Température initiale en K (≈10°C)
    sigma = 5.67e-8     # Constante de Stefan-Boltzmann
    dt = 3600           # Pas de temps en secondes (1h)
    A = get_mean_albedo(lat,lon)             # Albédo de la surface considérée (utiliser les modèle de l'année dernière pour déterminer alpha)
    h = 10              # Coefficient de transfert thermique vers l'air (W/m²·K)
    T_air = 283         # Température de l'air "ambiante" de référence (K)
    T = [T0]
    for i in range(len(P_recu)):
        flux_entrant = (1 - A) * P_recu[i] * S
        flux_sortant_rad = 0.5 * sigma * S * T[i]**4
        flux_convection = h * S * (T[i] - T_air)
        dT = dt * (flux_entrant - flux_sortant_rad - flux_convection) / c
        T.append(T[i] + dT)
    return T

def puissance_recue_par_heure(latitude_deg, longitude_deg, jour_de_l_annee):

    """
    Calcule la puissance reçue du Soleil heure par heure pour un point donné de la Terre.

    Entrées :
        - latitude_deg : latitude géographique en degrés (Nord positif)
        - longitude_deg : longitude en degrés (Est positif)
        - jour_de_l_annee : entier entre 1 et 365

    Sortie :
        - liste de 24 valeurs (en W/m²) correspondant à la puissance solaire reçue chaque heure
    """
    # Constante solaire (en W/m²), correspondant à la puissance totale émise par le soleil divisé par 4*pi*dTS**2 avec dTS distance Terre-Soleil
    S0 = 1361

    # Conversion angles
    lat = np.radians(latitude_deg)
    lon = np.radians(longitude_deg)

    # Inclinaison de l’axe terrestre
    inclinaison = np.radians(23.5)

    # Calcul de la déclinaison solaire (δ), approximation type NOAA
    # δ varie entre -23.5° et +23.5°
    declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2 * np.pi * (jour_de_l_annee - 81) / 365))

    # Vecteur direction du Soleil dans le repère terrestre à midi (z nord, x équateur)
    # Supposé dans le plan (x, z)

    soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)]) # projection équatoriale # composante nord-sud

    soleil /= np.linalg.norm(soleil)

    puissances = []

    for h in range(24):
        # Angle horaire de la Terre : 0° à midi local, -180° à 0h, +180° à 23h
        # Terme "rotation journalière" par rapport au méridien local

        angle_terre = np.radians(15 * (h - 12))# 15° par heure

        # Position du point à la surface de la Terre (coord. sphériques -> cartésiennes)
        x = np.cos(lat) * np.cos(lon + angle_terre)
        y = np.cos(lat) * np.sin(lon + angle_terre)
        z = np.sin(lat)

        normale = np.array([x, y, z])

        # Produit scalaire entre normale locale et direction du Soleil
        prod = np.dot(normale, soleil)
        puissances.append(max(0, S0 * prod))
    return puissances


def chaque_jour(lat, long):

    """
    Prends les coordonnée d'un point en entrée et renvoie la puissance recue par ce point au cours d'une année sous forme de Liste de sous listes, les sous-listes correspondant à chaqu journées
    """

    return [puissance_recue_par_heure(lat, long, j) for j in range(1, 366)]

def annee(P_tout):

    """
    Renvoie une liste de puissance heure par heure étalée sur une année
    """

    return [val for jour in P_tout for val in jour]


P_annuelle = annee(chaque_jour(lat, lon))
T_point = temp(P_annuelle)

# Dates : 8760 points (1 par heure sur 365 jours)
date_debut = datetime.datetime(2024, 1, 1)
dates = [date_debut + datetime.timedelta(hours=i) for i in range(len(T_point))]

# Affichage
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(dates, T_point)

# Localisateur et formateur automatiques pour zoom intelligent
locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)

ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)

plt.xlabel("Date")
plt.ylabel("Température (K)")
plt.title("Température au cours de l'année au point de latitude " + str(lat) + " et de longitude " + str(lon))
plt.grid(True)
plt.tight_layout()
plt.show()
