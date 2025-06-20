# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 17:21:55 2025

@author: jeann
"""
import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import librairie_puissances as l_p
import parametres_surface as p_s
import parametre_convection as p_c
import fonction_calcul_alpha as f_c


# ---------------------- Simulation Température ---------------------- #
def temp(lat = 48.85, long = 2.35):
    cm = p_s.classify_point(long, lat)
    rho = p_s.masse_volumique_point(long, lat)
    A = p_s.get_mean_albedo(lat, long)
    h = p_c.liste_h(lat,long)
    alpha = f_c.calcul_alpha(5.67e-8*(288)**4)
    print(alpha)
    d = 0.1 #10cm
    S = 1 #surface
    c = cm*rho*S*d
    T0 = 283
    dt = 3600
    T_air = 283
    T = [T0]
    
    for i in range(24*365):
        P_emis = l_p.P_em_surf_thermal(lat,long,i,T[i]) + l_p.P_em_surf_conv(lat,long,i, T[i], T_air, h[i]) + l_p.P_em_surf_evap(lat,long,i)
        P_recue = l_p.P_abs_surf_solar(lat,long,i,A) + l_p.P_em_atm_thermal_down(lat, long,i, alpha, P_emis) 
        dT = dt * (P_recue - P_emis) / c
        T.append(T[i] + dT)
    
    return T

if __name__ == "__main__":
    # Simulation température
    lat, long = 48.51, 2.20
    T_point = temp(lat, long)
    # ---------------------- Affichage ---------------------- #
    date_debut = datetime.datetime(2024, 1, 1)
    dates = [date_debut + datetime.timedelta(hours=i) for i in range(len(T_point))]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(dates, T_point)

    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    plt.xlabel("Date")
    plt.ylabel("Température (K)")
    plt.title(f"Température pour un point de coordonnées ({lat}°N, {long}°E)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()