#Cette librairie propose une convention pour le nom des puissances surfaciques considérées, mais n'a pas vocation à être réutilisée telle quelle.
# conventions:
# lat: float (radian), 0 is at equator, -pi/2 is at south pole, and +pi/2 is at north pole
# long: float (radian), 0 is at greenwich meridiant
# t: float (s), 0 is at 00:00 (greenwich time) january 1, 365*24*60*60 is at the end of the year, (maybe use 365.25? no idea what is best, or maybe use UTC ?)


import numpy as np
import math
import fonction_calcul_alpha as f_c
P0 = 1360  # W/m² – zenith irradiance at the top of the atmosphere
PHI = 0.409  # precession angle rad  (23.45 deg)
SIGMA = 5.67e-8  # W/m²K⁴ – Stefan-Boltzmann constant
S = 1 #surface

def P_inc_solar(lat: float, lon: float, t: float):
    S0 = 1361  # constante solaire
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    inclinaison = np.radians(23.5)

    # Convertir l’instant t (en heures) en jour et heure
    t_int = math.ceil(t)
    jour = t_int // 24 + 1  # jour entre 1 et 365
    heure = t_int % 24      # heure entre 0 et 23

    # Calcul des paramètres solaires à ce moment précis
    declinaison = np.arcsin(
        np.sin(inclinaison) * np.sin(2 * np.pi * (jour - 81) / 365)
    )
    soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
    soleil /= np.linalg.norm(soleil)

    angle_terre = np.radians(15 * (heure - 12))
    x = np.cos(lat_rad) * np.cos(lon_rad + angle_terre)
    y = np.cos(lat_rad) * np.sin(lon_rad + angle_terre)
    z = np.sin(lat_rad)
    normale = np.array([x, y, z])

    prod = np.dot(normale, soleil)
    return max(0, S0 * prod)

# Surface
def P_abs_surf_solar(lat: float, long: float, t: float, A):
    puissance_abs_surf_solar = (1 - A)* P_inc_solar(lat, long, t) * S
    return puissance_abs_surf_solar


def P_em_surf_thermal(lat: float, long: float, t: float, T: float):
    return SIGMA * (T**4)


def P_em_surf_conv(lat: float, long: float, t: float, T, T_air,h):
    return h * S * (T - T_air)

def P_em_surf_evap(lat: float, long: float, t: float):
    return 86

# atmosphere
def P_abs_atm_solar(lat: float, long: float, t: float, Pinc: float):
    AbsAtmo = 0.22
    return AbsAtmo * Pinc


def P_abs_atm_thermal(lat: float, long: float, t: float, T: float):
    return 358


def P_em_atm_thermal_up(lat: float, long: float, t: float):
    return 170


def P_em_atm_thermal_down(lat: float, long: float, t: float, alpha, P_emis):
   return (alpha/2)*P_emis
