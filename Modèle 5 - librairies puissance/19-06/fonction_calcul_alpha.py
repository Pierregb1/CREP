# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 11:12:27 2025

@author: jeann
"""
import Code_atmo_couche_backup as c_a

def calcul_alpha(P_emis):
    taux_co2_2024 = 415.6e-6 #en ppm
    flux_emis_terre = P_emis#en W/m^2
    lambda_range, z_range, upward_flux, optical_thickness = c_a.simulate_radiative_transfer(taux_co2_2024)
    mean_flux_top = upward_flux[-1,:].sum()
    alpha = mean_flux_top/flux_emis_terre
    return(alpha)