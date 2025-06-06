import math
import matplotlib.pyplot as plt

# ===================================================================
# 1) Définitions liées à l’albédo et au calcul radiatif (jour/nuit) 
# ===================================================================

# Constantes pour le calcul radiatif
S_solaire = 1361.0        # Constante solaire (W/m²)
sigma = 5.67e-8           # Constante de Stefan-Boltzmann (W/m²/K⁴)
omega = 2 * math.pi / 24  # Pulsation (rad/h) pour un cycle de 24 h

# Valeurs d’albédo pour différentes régions (comme dans Modele_3.py)
data_albedo = {
    "Amérique du Nord":         0.25,
    "Amérique du Sud":         0.18,
    "Europe de l'Ouest":       0.25,
    "Europe de l'Est":         0.30,
    "Asie du Sud":             0.15,
    "Asie de l'Est":           0.20,
    "Asie du Sud-Est":         0.20,
    "Afrique du Nord":         0.25,
    "Afrique Sub-saharienne":  0.18,
    "Afrique_Désertique":      0.45,
    "Océans":                  0.12,
    "Pole Nord":               0.75,
    "Pole Sud":                0.80
}

def determiner_partie_terre(lat, lon):
    """
    Renvoie la clé du dictionnaire d’albédo selon la latitude/longitude.
    """
    if lat >= 60:
        return "Pole Nord"
    elif lat <= -60:
        return "Pole Sud"
    elif 30 <= lat <= 60 and -130 <= lon <= -60:
        return "Amérique du Nord"
    elif -60 <= lat <= 15 and -90 <= lon <= -30:
        return "Amérique du Sud"
    elif 45 <= lat <= 70 and -10 <= lon <= 40:
        if -10 <= lon <= 20:
            return "Europe de l'Ouest"
        else:
            return "Europe de l'Est"
    elif -10 <= lat <= 40 and 60 <= lon <= 160:
        if 5 <= lat <= 30 and 60 <= lon <= 120:
            return "Asie du Sud"
        elif 30 <= lat <= 50 and 100 <= lon <= 140:
            return "Asie de l'Est"
        else:
            return "Asie du Sud-Est"
    elif 15 <= lat <= 30 and -20 <= lon <= 40:
        return "Afrique_Désertique"
    elif -35 <= lat <= 15 and -20 <= lon <= 50:
        if lat > 0:
            return "Afrique du Nord"
        else:
            return "Afrique Sub-saharienne"
    else:
        return "Océans"

def obtenir_albedo(lat, lon):
    """
    Rend l’albédo en fonction de la latitude et de la longitude.
    """
    partie = determiner_partie_terre(lat, lon)
    return data_albedo.get(partie, 0.12)  # Si absent, on prend Océans par défaut (0.12)

def calculate_temperature(S, A, sigma, lat, lon, t_decimal):
    """
    Calcule la température d’équilibre radiatif (en Kelvin) à l’heure t_decimal (heures décimales 0–24).
    - S          : constante solaire (W/m²)
    - A          : albédo local (sans unité, 0–1)
    - sigma      : constante de Stefan-Boltzmann (W/m²/K⁴)
    - lat, lon   : coordonnées du lieu
    - t_decimal  : heure locale en heures décimales (0 ≤ t_decimal < 24)
    
    Si le flux solaire local est négatif (nuit), on force l’énergie reçue à 0.
    Retourne T_eq en Kelvin.
    """
    # 1) Flux solaire moyen corrigé de l’albédo et d’un terme “effet de serre” (ici +244 W/m²)
    S4 = S / 4.0
    Salbedo = S4 * (1 - A)
    Salbedo_effet = Salbedo + 244.0

    # 2) On modélise l’angle d’incidence par un cosinus sur la journée + orientation géographique
    Sloc = Salbedo_effet * (
        math.cos(omega * t_decimal) * math.sin((90.0 - lat) * math.pi/180.0) * math.sin(lon * math.pi/180.0)
      + math.sin(omega * t_decimal) * math.sin((90.0 - lat) * math.pi/180.0) * math.cos(lon * math.pi/180.0)
    )

    # On force Sloc ≥ 0 (sinon c’est la nuit, donc pas de flux solaire direct)
    if Sloc < 0:
        energy_received = 0.0
    else:
        energy_received = Sloc

    # Loi de Stefan-Boltzmann → température d’équilibre radiatif (en K)
    T_eq = (energy_received / sigma) ** 0.25
    return T_eq


# ===================================================================
# 2) Votre code « tel quel » (avec juste un petit ajustement pour T_lim)
# ===================================================================

T0    = 100.0   # Température initiale (en °C)
t0    = 0.0     # Temps initial (en “unités arbitraires” que l’on interprète comme heures décimales)
N     = 1000    # Nombre d’itérations
dt    = 0.01    # Pas de temps (on l’interprète comme des heures décimales)
c     = 1.0     # Capacité thermique
h     = 0.1     # Coefficient de transfert
S     = 10.0    # Surface
# Remarque : on conserve la variable T_lim mais on ne l’utilisera plus de façon fixe. 
#           Sa valeur sera recalculée dynamiquement à chaque pas de temps.

# Choix d’une latitude/longitude (pour définir où l’on se trouve sur Terre)
lat = 48.8566   # Paris
lon = 2.3522

def Temp(T0, t0, N, dt, c, h, S, T_lim):
    """
    Simule l’évolution de la température en appliquant la loi de Newton,
    mais au lieu d’utiliser un T_lim constant, on remplace T_lim par une
    température d’équilibre radiatif calculée (jour/nuit).
    
    - T0     : Température initiale en °C
    - t0     : Temps initial (en h décimales, ex. 0 → minuit)
    - N      : Nombre de pas de temps
    - dt     : Pas de temps (en heures décimales)
    - c      : Capacité thermique
    - h      : Coefficient de transfert
    - S      : Surface
    - T_lim  : On le laisse en place pour la signature, 
               mais on recalcule dynamiquement à l’intérieur.
               
    Renvoie (t, T) :
      - t : liste des temps (en heures décimales depuis t0)
      - T : liste des températures (en °C)
    """
    # On calcule une seule fois l’albédo local (puisqu’il ne change pas au cours de la simulation)
    A_local = obtenir_albedo(lat, lon)

    T = [T0]       # Températures en °C
    t = [t0]       # Temps en heures décimales

    for i in range(1, N):
        # 1) Mise à jour du temps
        nouveau_t = t[i-1] + dt
        t.append(nouveau_t)

        # 2) On calcule la température d’équilibre radiatif en Kelvin à l’instant nouveau_t
        #    Note : on prend (nouveau_t % 24) pour cycler sur 0–24 h
        T_eq_K = calculate_temperature(
            S_solaire,      # Constante solaire
            A_local,        # Albédo local
            sigma,          # Constante Stefan-Boltzmann
            lat, lon,       # Position géographique
            nouveau_t % 24  # Heure locale en heures décimales (0–24)
        )

        # 3) Conversion en °C pour qu’on reste cohérent avec T (qui est en °C)
        T_eq_C = T_eq_K - 273.15

        # 4) On applique la loi de Newton avec T_lim = T_eq_C
        T_prev = T[i-1]
        dT = - (h * S / c) * (T_prev - T_eq_C) * dt
        T_new = T_prev + dT
        T.append(T_new)

    return (t, T)


# ===================================================================
# 3) Exécution de la simulation et tracé (idem à votre code d’origine)
# ===================================================================

# On appelle Temp en lui passant T_lim (valeur initiale, mais elle sera réécrite à chaque pas)
t_liste, T_liste = Temp(T0, t0, N, dt, c, h, S, T_lim=20.0)

# On trace exactement comme avant
plt.plot(t_liste, T_liste, linewidth=1.2)
plt.xlabel('Temps (h décimales depuis t0)', fontsize=12)
plt.ylabel('Température (°C)', fontsize=12)
plt.title('Température en fonction du temps (avec cycle jour/nuit)', fontsize=14)
plt.grid()
plt.show()
