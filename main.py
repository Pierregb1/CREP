
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import datetime
import math
import io

app = Flask(__name__)

# ---------- OUTILS COMMUNS ----------
def puissance(lat, lon, jour):
    S0 = 1361
    lat = math.radians(lat)
    lon = math.radians(lon)
    inclinaison = math.radians(23.5)
    declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2 * math.pi * (jour - 81) / 365))
    soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
    soleil /= np.linalg.norm(soleil)
    puissances = []
    for h in range(24):
        angle = math.radians(15 * (h - 12))
        x = np.cos(lat) * np.cos(lon + angle)
        y = np.cos(lat) * np.sin(lon + angle)
        z = np.sin(lat)
        normale = np.array([x, y, z])
        puissances.append(max(0, S0 * np.dot(normale, soleil)))
    return puissances

def chaque_jour(lat, lon):
    return [puissance(lat, lon, j) for j in range(1, 366)]

def annee(P):
    return [val for jour in P for val in jour]

def temp(P_recu, c):
    S = 1
    T0 = 273
    sigma = 5.67e-8
    dt = 3600
    A = 0.3
    T = [T0]
    for i in range(len(P_recu)):
        flux_sortant = 0.5 * sigma * S * (T[i])**4
        T.append(T[i] + dt * ((1 - A) * P_recu[i] * S - flux_sortant) / c)
    return T

def trim_data(dates, T, scale):
    if scale == "month":
        return dates[:24*30 + 1], T[:24*30 + 1]
    elif scale == "day":
        return dates[:24 + 1], T[:24 + 1]
    return dates, T

# ---------- MODÈLE 1 ----------
def run_model1(zoomX):
    fig, ax = plt.subplots()
    time_max = 24 / zoomX
    x = np.linspace(0, time_max, 1000)
    y = 273 + 10 * np.exp(-x / 5)
    ax.plot(x, y)
    ax.set_title("Modèle 1 : Refroidissement simple")
    ax.set_xlabel("Temps (heures)")
    ax.set_ylabel("Température (K)")
    ax.grid(True)
    return fig

# ---------- MODÈLES 2, 3, 4 ----------
def run_model_generic(lat, lon, c, model_id, scale):
    P = annee(chaque_jour(lat, lon))
    T = temp(P, c)
    dates = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
    dates, T = trim_data(dates, T, scale)
    fig, ax = plt.subplots()
    ax.plot(dates, T)
    ax.set_title(f"Modèle {model_id} — {scale}")
    ax.set_xlabel("Temps")
    ax.set_ylabel("Température (K)")
    ax.grid(True)
    fig.autofmt_xdate()
    return fig

# ---------- API ----------
@app.route("/run")
def run():
    model = int(request.args.get("model", 1))
    zoomX = float(request.args.get("zoomX", 1.0))
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    scale = request.args.get("scale", "year")

    if model == 1:
        fig = run_model1(zoomX)
    elif model == 2:
        fig = run_model_generic(lat, lon, 2.25e5, 2, scale)
    elif model == 3:
        fig = run_model_generic(lat, lon, 1.5e5, 3, scale)
    elif model == 4:
        fig = run_model_generic(lat, lon, 3e5, 4, scale)
    else:
        return "Modèle inconnu", 400

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
