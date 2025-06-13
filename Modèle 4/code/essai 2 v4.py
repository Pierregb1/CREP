import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates

def coefficient_convection(v):
    """
    Calcule le coefficient de convection thermique (h) à partir de la vitesse du vent (v en m/s).
    Retourne h en W/m²·K
    """
    rho = 1.2         # Masse volumique de l'air (kg/m³)
    mu = 1.8e-5       # Viscosité dynamique de l'air (Pa·s)
    L = 1.0           # Longueur caractéristique (m)
    Pr = 0.71         # Nombre de Prandtl pour l'air
    lambda_air = 0.026  # Conductivité thermique de l'air (W/m·K)

    Re = rho * v * L / mu

    if Re < 5e5:
        C, m, n = 0.664, 0.5, 1/3  # Régime laminaire
    else:
        C, m, n = 0.037, 0.8, 1/3  # Régime turbulent

    Nu = C * Re**m * Pr**n
    h = Nu * lambda_air / L
    return h

def vent_moyen_par_jour(latitude_deg):
    """
    Estimation journalière simplifiée de la vitesse moyenne du vent (m/s),
    selon la latitude et la saison.
    """
    latitude_rad = np.radians(latitude_deg)
    return [2 + 2.5 * np.cos(latitude_rad) + 1.5 * np.cos(2 * np.pi * (j - 81) / 365) for j in range(1, 366)]

def temp(P_recu, vitesses_vent_journalières):
    """
    Calcule la température du sol heure par heure en tenant compte du vent.
    Entrées :
        - P_recu : liste de puissances solaires reçues (W/m²) heure par heure (8760 valeurs)
        - vitesses_vent_journalières : liste de vitesses moyennes du vent pour chaque jour (365 valeurs)
    Sortie :
        - Liste de températures (K), heure par heure (8761 valeurs)
    """
    c = 2.25e5        # Capacité thermique (J/K)
    S = 1             # Surface (m²)
    T0 = 283          # Température initiale (K)
    sigma = 5.67e-8   # Constante de Stefan-Boltzmann
    dt = 3600         # Pas de temps (s)
    A = 0.3           # Albédo
    T_air = 283       # Température de l'air ambiant (K)

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

def puissance_recue_par_heure(latitude_deg, longitude_deg, jour_de_l_annee):
    """
    Calcule la puissance solaire reçue heure par heure pour une date et un lieu.
    """
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

def chaque_jour(lat, long):
    """
    Retourne la liste de puissances reçues heure par heure pour chaque jour de l'année.
    """
    return [puissance_recue_par_heure(lat, long, j) for j in range(1, 366)]

def annee(P_tout):
    """
    Aplati une liste de 365 listes horaires (par jour) en une seule liste horaire (8760 valeurs).
    """
    return [val for jour in P_tout for val in jour]

# Coordonnées de Paris
lat, lon = 48.85, 2.35

# Données de puissance et de vent
P_annuelle = annee(chaque_jour(lat, lon))
vent_journalier = vent_moyen_par_jour(lat)

# Simulation de température
T_point = temp(P_annuelle, vent_journalier)

# Génération des dates pour l'affichage (8760 heures + 1)
date_debut = datetime.datetime(2024, 1, 1)
dates = [date_debut + datetime.timedelta(hours=i) for i in range(len(T_point))]

# Affichage de la température simulée
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(dates, T_point, label="Paris")

locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)

plt.xlabel("Date")
plt.ylabel("Température du sol (K)")
plt.title("Évolution de la température au cours de l'année à Paris")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
