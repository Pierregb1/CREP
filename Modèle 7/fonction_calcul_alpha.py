# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 11:12:27 2025

@author: jeann
"""
import Code_atmo_couche_backup as c_a

def concentration_CO2(annee):
    """
    Renvoie la concentration estimée de CO₂ en ppm pour une année donnée.
    """
    if 1838 <= annee <= 1972:
        return 0.294 * annee - 262
    elif annee < 1952:
        return 278  # valeur moyenne avant l'ère industrielle
    else:
        return 1.9 * annee - 3430  # modèle linéaire post-1952

def calcul_alpha(P_emis, annee):
    taux_co2 = concentration_CO2(annee)
    taux_co2_ppm = taux_co2*1e-6#en ppm
    lambda_range, z_range, upward_flux, optical_thickness, earth_flux = c_a.simulate_radiative_transfer(taux_co2_ppm)
    mean_flux_top = upward_flux[-1,:].sum()
    flux_emis_terre = P_emis #en W/m^2
    alpha = mean_flux_top/flux_emis_terre
    return(alpha)
