
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import io
import datetime
import math

app = Flask(__name__)

def generer_graphique_zoome(x, y, zoomX=1.0, offset=0.0, titre="Graphique", xlabel="Temps", ylabel="Valeur"):
    """
    zoomX : facteur de zoom (>1 = zoom avant)
    offset : fraction entre 0 et 1 représentant le début de la fenêtre d'affichage
    """
    fig, ax = plt.subplots()
    n = len(x)
    window = max(1, int(n / zoomX))
    start_idx = int(offset * (n - window))
    end_idx = start_idx + window
    x_zoom = x[start_idx:end_idx]
    y_zoom = y[start_idx:end_idx]
    ax.plot(x_zoom, y_zoom)
    ax.set_title(titre)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    return fig

def run_model1(zoomX=1.0, offset=0.0):
    time_total = 24  # heures
    n_points = 1000
    x = np.linspace(0, time_total, n_points)
    y = 273 + 10 * np.exp(-x / 5)
    return generer_graphique_zoome(x, y, zoomX, offset, "Modèle 1 : Refroidissement", "Temps (heures)", "Température (K)")

def calc_model_temp(lat, lon, c):
    def puissance(lat, lon, jour):
        S0 = 1361
        lat_r = math.radians(lat)
        lon_r = math.radians(lon)
        inclinaison = math.radians(23.5)
        declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2 * math.pi * (jour - 81) / 365))
        soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
        soleil /= np.linalg.norm(soleil)
        puissances = []
        for h in range(24):
            angle = math.radians(15 * (h - 12))
            x = np.cos(lat_r) * np.cos(lon_r + angle)
            y = np.cos(lat_r) * np.sin(lon_r + angle)
            z = np.sin(lat_r)
            normale = np.array([x, y, z])
            puissances.append(max(0, S0 * np.dot(normale, soleil)))
        return puissances

    P = [val for jour in (puissance(lat, lon, j) for j in range(1, 366)) for val in jour]
    S = 1
    T0 = 273
    sigma = 5.67e-8
    dt = 3600
    A = 0.3
    T = [T0]
    for i in range(len(P)):
        flux_sortant = 0.5 * sigma * S * (T[i])**4
        T.append(T[i] + dt * ((1 - A) * P[i] * S - flux_sortant) / c)
    dates = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
    return dates, T

def run_model_generic(lat, lon, c, zoomX=1.0, offset=0.0, titre="Modèle"):
    dates, T = calc_model_temp(lat, lon, c)
    return generer_graphique_zoome(dates, T, zoomX, offset, titre, "Temps", "Température (K)")

@app.route("/run")
def run():
    model = int(request.args.get("model", 1))
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    zoomX = float(request.args.get("zoomX", 1.0))
    offset = float(request.args.get("offset", 0.0))

    if model == 1:
        fig = run_model1(zoomX, offset)
    elif model == 2:
        fig = run_model_generic(lat, lon, 2.25e5, zoomX, offset, "Modèle 2 — Température annuelle (c=2.25e5)")
    elif model == 3:
        fig = run_model_generic(lat, lon, 1.5e5, zoomX, offset, "Modèle 3 — Température annuelle (c=1.5e5)")
    elif model == 4:
        fig = run_model_generic(lat, lon, 3e5, zoomX, offset, "Modèle 4 — Température annuelle (c=3e5)")
    else:
        return "Modèle inconnu", 400

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
