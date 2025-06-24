import numpy as np
S0 = 1361
sigma, dt = 5.67e-8, 3600

def _puissance_heure(lat, lon, j):
    lat, lon = np.radians(lat), np.radians(lon)
    incl = np.radians(23.5)
    decl = np.arcsin(np.sin(incl)*np.sin(2*np.pi*(j-81)/365))
    sun = np.array([np.cos(decl), 0, np.sin(decl)])
    sun /= np.linalg.norm(sun)
    out = []
    for h in range(24):
        ang = np.radians(15*(h-12))
        n = [np.cos(lat)*np.cos(lon+ang),
             np.cos(lat)*np.sin(lon+ang),
             np.sin(lat)]
        out.append(max(0, S0*np.dot(n, sun)))
    return out

def _annee(lat, lon):
    return [val for j in range(1,366) for val in _puissance_heure(lat, lon, j)]

def temp(lat, lon):
    P = _annee(lat, lon)
    c, S, A, T = 2.25e5, 1, 0.3, [273]
    for i in range(len(P)-1):
        flux_out = 0.5*sigma*S*T[i]**4
        T.append(T[i] + dt*((1-A)*P[i]*S - flux_out)/c)
    return T
