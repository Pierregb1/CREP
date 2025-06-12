import numpy as np
import matplotlib.pyplot as plt

def temp(P_recu):

    """
    renvoie une liste de température à partir d'une liste de puissance recue
    entrée: Liste de puissances reçues au cours du temps
    sortie: Liste de températures évaluées en fonction du temps

    """

    c = 2.25e5    # Capacité thermique (J/K)
    alpha = 0        # Effet de serre (inutile ici car alpha=0) chercher modèle
    S = 1            # Surface (m²)
    T0 = 273        # Température initiale en K
    sigma = 5.67e-8  # Constante de Stefan-Boltzmann
    dt = 3600        # Pas de temps en secondes (1h)
    A = 0.3            # Albédo de la surface considérée (utiliser les modèle de l'année dernière pour déterminer alpha)

    T = [T0]
    for i in range(len(P_recu) - 1):
        flux_sortant = 0.5*sigma * S * (T[i])**4
        T_apres = T[i] + dt * ((1-A)*P_recu[i]*S - flux_sortant) / c #premier principe appliqué au système bloc de Terre au niveau du sol
        T.append(T_apres)
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
    soleil = np.array([
        np.cos(declinaison),  # projection équatoriale
        0,
        np.sin(declinaison)   # composante nord-sud
    ])
    soleil /= np.linalg.norm(soleil)

    puissances = []

    for h in range(24):
        # Angle horaire de la Terre : 0° à midi local, -180° à 0h, +180° à 23h
        # Terme "rotation journalière" par rapport au méridien local
        angle_terre = np.radians(15 * (h - 12))  # 15° par heure

        # Position du point à la surface de la Terre (coord. sphériques -> cartésiennes)
        x = np.cos(lat) * np.cos(lon + angle_terre)
        y = np.cos(lat) * np.sin(lon + angle_terre)
        z = np.sin(lat)
        normale = np.array([x, y, z])

        # Produit scalaire entre normale locale et direction du Soleil
        prod = np.dot(normale, soleil)
        puissance = max(0, S0 * prod)
        puissances.append(puissance)

    return puissances

#pour simuler plusieur fois d'affilée le même jour
def liste(l):
    L = []
    for j in range(10):
        for i in range (len(l)):
            L.append(l[i])
    return(L)


def chaque_jour(lat,long):

    """
    Prends les coordonnée d'un point en entrée et renvoie la puissance recue par ce point au cours d'une année (sous forme de listes de sous-listes, les sous-listes correspondant à chaque journée)
    """

    P_tout_jour = [] #température de chaque journée
    for i in range(1,366):
        P_jour = puissance_recue_par_heure(lat,long,i)
        P_tout_jour.append(P_jour)
    return(P_tout_jour)

def annee(P_tout):

    """
    Renvoie une liste de puissance heure par heure, étalée sur une année
    """

    P = []
    for i in range(len(P_tout)):
        for j in range(len(P_tout[i])):
            P.append(P_tout[i][j])
    return(P)

# Exemple : Paris, 48.85°N, 2.35°E, 21 juin (jour 172)
P_paris = puissance_recue_par_heure(48.85, 2.35, 172)
T_point = temp(annee(chaque_jour(48.85,2.35)))
# Affichage
plt.plot(range(len(T_point)), T_point)
plt.xlabel("Heure")
plt.ylabel("température point K")
plt.title("température du point le 21 juin")
plt.grid()
plt.show()
