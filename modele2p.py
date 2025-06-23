import numpy as np
def puissance_recue_par_heure(latitude_deg, longitude_deg, jour):
    S0 = 1361
    lat = np.radians(latitude_deg); lon = np.radians(longitude_deg)
    incl = np.radians(23.5)
    decl = np.arcsin(np.sin(incl) * np.sin(2*np.pi*(jour-81)/365))
    soleil = np.array([np.cos(decl), 0, np.sin(decl)]); soleil /= np.linalg.norm(soleil)
    puiss = []
    for h in range(24):
        angle = np.radians(15*(h-12))
        x = np.cos(lat)*np.cos(lon+angle); y = np.cos(lat)*np.sin(lon+angle); z = np.sin(lat)
        normale = np.array([x, y, z]); prod = np.dot(normale, soleil)
        puiss.append(max(0, S0*prod))
    return puiss

def chaque_jour(lat, lon):
    return [puissance_recue_par_heure(lat, lon, j) for j in range(1, 366)]

def annee(P):
    return [val for jour in P for val in jour]

def _temp_from_P(P_recu, c=2.25e5):
    sigma, S, dt, A = 5.67e-8, 1, 3600, 0.3
    T = [273]
    for i in range(len(P_recu)-1):
        flux_out = 0.5*sigma*S*T[i]**4
        T.append(T[i] + dt*((1-A)*P_recu[i]*S - flux_out)/c)
    return T

def temp(lat, lon):
    P_annuelle = annee(chaque_jour(lat, lon))
    return _temp_from_P(P_annuelle)
