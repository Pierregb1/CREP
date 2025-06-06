import numpy as np
import matplotlib.pyplot as plt

# 1. Constantes physiques
sigma = 5.670374419e-8  # Constante de Stefan-Boltzmann (W/m²/K^4)
S0 = 1361               # Constante solaire (W/m²)
alpha = 0.3             # Albédo moyen de la Terre
a = 0.39                # Facteur de piégeage radiatif (effet de serre)
C = 4.2e8               # Capacité calorifique par unité de surface (J/m²/K)

# 2. Fonction dérivée dT/dt
def dT_dt(T):
    # Flux entrant par unité de surface
    Qin = S0 * (1 - alpha) / 4
    # Flux sortant modifié par l'effet de serre
    Qout = (1 - a) * sigma * T**4
    # Équation différentielle
    return (Qin - Qout) / C

# 3. Conditions initiales
T0 = 280.0  # Température initiale (K)
t_max = 50 * 365 * 24 * 3600  # Durée de simulation : 50 ans en secondes
dt = 30 * 24 * 3600           # Pas de temps : 1 mois en secondes
N_steps = int(t_max / dt)

# Tableaux pour stocker les résultats
ts = np.linspace(0, t_max, N_steps + 1)  # Temps (s)
Ts = np.zeros(N_steps + 1)               # Températures (K)
Ts[0] = T0

# 4. Intégration par méthode d'Euler
for i in range(N_steps):
    Ts[i+1] = Ts[i] + dT_dt(Ts[i]) * dt

# Conversion du temps en années pour le tracé
ts_years = ts / (365 * 24 * 3600)

# 5. Tracé de la température en fonction du temps
plt.figure(figsize=(10, 6))
plt.plot(ts_years, Ts, label="Température globale moyenne (K)")
plt.xlabel("Temps (années)")
plt.ylabel("Température (K)")
plt.title("Évolution de la température terrestre (modèle EBM simple)")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()
