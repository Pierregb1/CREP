
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import io, datetime, math

app = Flask(__name__)

# ------------------------------------------------------------
# OUTILS COMMUNS
# ------------------------------------------------------------
def puissance(lat, lon, jour):
    """Flux horaire reçu pour un jour donné (liste de 24 valeurs)."""
    S0 = 1361                                    # constante solaire (W/m²)
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    incl = math.radians(23.5)                    # inclinaison de l'axe terrestre
    # déclinaison solaire
    dec = math.asin(math.sin(incl) * math.sin(2*math.pi*(jour-81)/365))
    soleil = np.array([math.cos(dec), 0, math.sin(dec)])
    soleil /= np.linalg.norm(soleil)             # vecteur normalisé

    puissances = []
    for h in range(24):
        angle = math.radians(15*(h-12))          # 0° à midi solaire
        x = math.cos(lat_r)*math.cos(lon_r+angle)
        y = math.cos(lat_r)*math.sin(lon_r+angle)
        z = math.sin(lat_r)
        normale = np.array([x, y, z])
        puissances.append(max(0, S0*np.dot(normale, soleil)))
    return puissances

def chaque_jour(lat, lon):
    return [puissance(lat, lon, j) for j in range(1, 366)]

def annee(P):
    """Aplatissement : 365 listes de 24 valeurs -> 8760 valeurs"""
    return [val for jour in P for val in jour]

def temp(P, c):
    """Évolution de température pour un flux horaire P (J/h)"""
    S = 1
    T0 = 288                                   # 15 °C initial
    sigma = 5.67e-8
    dt = 3600
    A = 0.3                                    # albédo
    T = [T0]
    for i, P_in in enumerate(P):
        flux_out = 0.5 * sigma * S * (T[i]**4)
        dT = dt * ((1-A)*P_in*S - flux_out) / c
        T.append(T[i] + dT)
    return T

def decouper_echelle(dates, T, scale):
    if scale == "month":
        n = 24*30                    # ~30 jours
    elif scale == "day":
        n = 24                       # 24 h
    else:                            # "year"
        return dates, T
    return dates[:n+1], T[:n+1]      # +1 pour inclure T0

# ------------------------------------------------------------
# MODÈLE 1 : refroidissement simple
# ------------------------------------------------------------
def run_model1(zoomX=1.0):
    fig, ax = plt.subplots()
    time_max = 24/zoomX
    x = np.linspace(0, time_max, 1000)
    y = 273 + 10*np.exp(-x/5)
    ax.plot(x, y)
    ax.set_title("Modèle 1 : refroidissement")
    ax.set_xlabel("Temps (h)")
    ax.set_ylabel("Température (K)")
    ax.grid(True)
    return fig

# ------------------------------------------------------------
# MODÈLES 2‑3‑4
# ------------------------------------------------------------
def build_model(lat, lon, c, scale, model_id):
    P = annee(chaque_jour(lat, lon))
    T = temp(P, c)
    dates = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
    dates, T = decouper_echelle(dates, T, scale)

    fig, ax = plt.subplots()
    ax.plot(dates, T)
    ax.set_title(f"Modèle {model_id} — {scale}")
    ax.set_xlabel("Temps")
    ax.set_ylabel("Température (K)")
    ax.grid(True)
    fig.autofmt_xdate()
    return fig

# ------------------------------------------------------------
# ROUTE API
# ------------------------------------------------------------
@app.route("/run")
def run():
    model = int(request.args.get("model", 1))
    scale = request.args.get("scale", "year")
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    zoomX = float(request.args.get("zoomX", 1.0))

    if model == 1:
        fig = run_model1(zoomX)
    elif model == 2:
        fig = build_model(lat, lon, 2.25e5, scale, 2)
    elif model == 3:
        fig = build_model(lat, lon, 1.5e5, scale, 3)
    elif model == 4:
        fig = build_model(lat, lon, 3e5, scale, 4)
    else:
        return "Modèle inconnu", 400

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
