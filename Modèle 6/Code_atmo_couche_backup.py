# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 16:21:27 2025

@author: danab
"""
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------

# ===================
# BLACKBODY RADIATION
# ===================

# Calcule la luminance spectrale émise par un corps noir à la température T pour chaque longueur d'onde
def planck_function(lambda_wavelength, T):
    h = 6.62607015e-34      # Constante de Planck, J*s
    c = 2.998e8             # Vitesse de la lumière, m/s
    kB = 1.380649e-23       # Constante de Boltzmann, J/K
    term1 = (2 * h * c**2) / lambda_wavelength**5
    term2 = np.exp((h * c) / (lambda_wavelength * kB * T)) - 1
    return term1 / term2

# ----------------------------------------------------------------------------------------------------------------------

# ================
# ATMOSPHERE MODEL
# ================

# Calcule la pression atmosphérique à une altitude z selon un modèle exponentiel (modèle barométrique isotherme)
def pressure(z):
    P0 = 101325     # Pression au niveau de la mer en Pa
    H = 8500        # Hauteur de l’échelle en m
    return P0 * np.exp(-z / H)

# Température constante (modèle simplifié)
def temperature_uniform(z):
    T0 = 288.2
    return T0 * np.ones_like(z)

# Décroissance linéaire jusqu’à la tropopause (11 km), puis constante
def temperature_simple(z):
    T0 = 288.2     # Température au niveau de la mer en K
    z_trop = 11000  # Hauteur de la tropopause en m
    Gamma = -0.0065 # Gradient de température en K/m
    T_trop = T0 + Gamma * z_trop
    return np.piecewise(z, [z < z_trop, z >= z_trop],
                        [lambda z: T0 + Gamma * z,
                         lambda z: T_trop])

# Modèle réaliste par couches, inspiré de l’atmosphère standard 1976
def temperature_US1976(z):
    z_km = z/1000  # Convertir l'altitude en km pour faciliter les comparaisons

    # Troposphère (0 à 11 km)
    T0 = 288.15
    z_trop = 11

    # Tropopause (11 à 20 km)
    T_tropopause = 216.65
    z_tropopause = 20

    # Stratosphère 1 (20 à 32 km)
    T_strat1 = T_tropopause
    z_strat1 = 32

    # Stratosphère 2 (32 à 47 km)
    T_strat2 = 228.65
    z_strat2 = 47

    # Stratopause (47 à 51 km)
    T_stratopause = 270.65
    z_stratopause = 51

    # Mésosphère 1 (51 à 71 km)
    T_meso1 = T_stratopause
    z_meso1 = 71

    # Mésosphère 2 (au-delà de 71 km)
    T_meso2 = 214.65

    return np.piecewise(z_km,
                        [z_km < z_trop,
                         (z_km >= z_trop) & (z_km < z_tropopause),
                         (z_km >= z_tropopause) & (z_km < z_strat1),
                         (z_km >= z_strat1) & (z_km < z_strat2),
                         (z_km >= z_strat2) & (z_km < z_stratopause),
                         (z_km >= z_stratopause) & (z_km < z_meso1),
                         z_km >= z_meso1],
                        [lambda z: T0 - 6.5 * z,
                         lambda z: T_tropopause,
                         lambda z: T_strat1 + 1 * (z - z_tropopause),
                         lambda z: T_strat2 + 2.8 * (z - z_strat1),
                         lambda z: T_stratopause,
                         lambda z: T_meso1 - 2.8 * (z - z_stratopause),
                         lambda z: T_meso2 - 2 * (z - z_meso1)])

# ==> CHOISIR ICI LE MODÈLE DE TEMPÉRATURE À UTILISER
def temperature(z):
    return temperature_simple(z)

# Calcule la densité moléculaire de l’air (nombre de molécules par m³) via l’équation des gaz parfaits
def air_number_density(z):
    kB = 1.380649e-23  # Constante de Boltzmann, J/K
    return pressure(z) / (kB * temperature(z))

# ----------------------------------------------------------------------------------------------------------------------

# ================
# CO2 ABSORPTION
# ================

# Modèle simplifié de l'absorption infrarouge du CO₂ autour de la longueur d’onde de 15 μm
def cross_section_CO2(wavelength):
    LAMBDA_0 = 15.0e-6  # Centre de la bande d’absorption infrarouge principale du CO₂ (en m)
    exponent = -22.5 - 24 * np.abs((wavelength - LAMBDA_0) / LAMBDA_0)  # Exposant décroissant avec l’écart à la bande centrale
    sigma = 10 ** exponent  # Convertit l’exposant en valeur réelle (section efficace)
    return sigma  # Renvoie les sections efficaces d’absorption (en m²/molécule)

# ----------------------------------------------------------------------------------------------------------------------

# =============================
# RADIATIVE TRANSFER SIMULATION
# =============================

# Toutes les longueurs d’onde sont traitées en parallèle grâce à la vectorisation

# Simule le transfert du rayonnement infrarouge émis par la Terre vers le sommet de l’atmosphère
def simulate_radiative_transfer(CO2_fraction, z_max = 80000, delta_z = 10, lambda_min = 0.1e-6, lambda_max = 100e-6, delta_lambda = 0.01e-6):

    # Grilles d’altitude et de longueur d’onde
    z_range = np.arange(0, z_max, delta_z)
    lambda_range = np.arange(lambda_min, lambda_max, delta_lambda)

    # Initialisation des tableaux
    upward_flux = np.zeros((len(z_range), len(lambda_range)))
    optical_thickness = np.zeros((len(z_range), len(lambda_range)))

    # Condition aux limites : calcul du flux vertical émis par la surface terrestre pour chaque longueur d’onde
    earth_flux = np.pi * planck_function(lambda_range, temperature(0)) * delta_lambda
    print(f"Total earth surface flux in wavelength range: {earth_flux.sum():.2f} W/m^2")

    flux_in = earth_flux
    for i, z in enumerate(z_range):
        # Pour chaque couche de l'atmosphère :
        # Densité de molécules de CO2
        n_CO2 = air_number_density(z) * CO2_fraction

        # Coefficient d’absorption (en 1/m)
        kappa = cross_section_CO2(lambda_range) * n_CO2

        # Calcul des flux dans la couche
        optical_thickness[i,:] = kappa * delta_z
        absorbed_flux = np.minimum(kappa * delta_z * flux_in , flux_in)
        emitted_flux = optical_thickness[i,:] * np.pi * planck_function(lambda_range, temperature(z)) * delta_lambda
        upward_flux[i, :] = flux_in - absorbed_flux + emitted_flux

        # Le flux sortant de la couche devient le flux incident sur la suivante
        flux_in = upward_flux[i, :]

    print(f"Total outgoing flux at the top of the atmosphere: {upward_flux[-1,:].sum():.2f} W/m^2")

<<<<<<< HEAD
<<<<<<< HEAD
    return lambda_range, z_range, upward_flux, optical_thickness, earth_flux

#----------------------------------------------------------------------------------------------------------------------

#MAIN
 
CO2_fraction = 415.6e-6
lambda_range, z_range, upward_flux, optical_thickness = simulate_radiative_transfer(CO2_fraction)
CO2_fraction = 815e-6
lambda_range, z_range, upward_flux2, optical_thickness2 = simulate_radiative_transfer(CO2_fraction)

# Plot top of atmosphere spectrum
plt.figure(figsize=(14, 9))
# Superimpose blackbody spectrum at Earth's surface temperature and 220K
plt.plot(1e6 * lambda_range, np.pi * planck_function(lambda_range, temperature(0))/1e6,'--k')
plt.plot(1e6 * lambda_range, np.pi * planck_function(lambda_range, 216)/1e6,'--k')

delta_lambda = lambda_range[1] - lambda_range[0]
plt.plot(1e6 * lambda_range, upward_flux[-1, :]/delta_lambda/1e6,'-g')
plt.plot(1e6 * lambda_range, upward_flux2[-1, :]/delta_lambda/1e6,'-r')
plt.fill_between(1e6 * lambda_range, upward_flux[-1, :]/delta_lambda/1e6, upward_flux2[-1, :]/delta_lambda/1e6, color='yellow', alpha=0.9)
plt.xlabel("Longueur d'onde (μm)")
plt.ylabel("Luminance spectrale (W/m²/μm/sr)")
plt.xlim(0, 50)
plt.ylim(0, 30)
plt.grid(True)
plt.show()
#----------------------------------------------------------------------------------------------------------------------
=======
    return lambda_range, z_range, upward_flux, optical_thickness, earth_flux
>>>>>>> dfb3cf894a55205a9c3b7edb316a37680abcc5fb
=======
    return lambda_range, z_range, upward_flux, optical_thickness, earth_flux
>>>>>>> 63930814a6f8ce10a0d832fd85bbde5c5f03007d
