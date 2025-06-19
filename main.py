
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import datetime, math, io

app = Flask(__name__)

# ---------- Outils communs ----------
S0 = 1361                        # Constante solaire
INCLINAISON = math.radians(23.5)
SIGMA = 5.67e-8

# -- Modèle 1 : refroidissement exponentiel simple
def modele1_series():
    t_h = np.linspace(0, 24, 1000)
    T   = 273 + 10 * np.exp(-t_h / 5)
    return t_h, T

# -- Outils pour les modèles 2‑3‑4 (simulation annuelle avec différentes capacités)
def puissance_jour(lat, lon, jour):
    lat = math.radians(lat)
    lon = math.radians(lon)
    declinaison = np.arcsin(np.sin(INCLINAISON) * np.sin(2 * math.pi * (jour - 81) / 365))
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

def puissance_annee(lat, lon):
    return [val for jour in range(1, 366) for val in puissance_jour(lat, lon, jour)]

def temperature(P_recu, c):
    S = 1
    T0 = 273
    dt = 3600
    A = 0.3
    T = [T0]
    for P in P_recu:
        flux_sortant = 0.5 * SIGMA * S * (T[-1])**4
        T.append(T[-1] + dt * ((1 - A) * P * S - flux_sortant) / c)
    return np.array(T)

# ---------- Route /run inchangée pour compatibilité ----------
@app.route("/run")
def run_old():
    model = int(request.args.get("model", 1))
    lat   = float(request.args.get("lat", 48.85))
    lon   = float(request.args.get("lon", 2.35))
    fig, ax = plt.subplots()
    if model == 1:
        x, y = modele1_series()
        ax.plot(x, y)
        ax.set_xlabel("Temps (h)")
    else:
        P  = puissance_annee(lat, lon)
        c_map = {2:2.25e5, 3:1.5e5, 4:3e5}
        T  = temperature(P, c_map.get(model, 2.25e5))
        dates = [datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
        ax.plot(dates, T)
        ax.set_xlabel("Temps")
    ax.set_ylabel("Température (K)")
    ax.set_title(f"Modèle {model}")
    ax.grid(True)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")

# ---------- Nouvelle fonction : 3 zooms ----------
def graphiques_multi_zoom(model, lat, lon):
    """Retourne un buffer PNG contenant 3 sous‑graphiques à 3 échelles"""
    if model == 1:
        x = np.linspace(0, 24, 1000)
        T = 273 + 10 * np.exp(-x / 5)
        time_array = x  # en heures
        unit = "h"
    else:
        P = puissance_annee(lat, lon)
        c_map = {2:2.25e5, 3:1.5e5, 4:3e5}
        T = temperature(P, c_map.get(model, 2.25e5))
        time_array = [datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
        unit = ""  # datetime
    # Création figure
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    # Annual
    axes[0].plot(time_array, T)
    axes[0].set_title("Échelle annuelle")
    # Monthly (30j)
    if model == 1:
        idx_m = (x <= 24)  # tout repris (pas pertinent pour modèle 1)
        axes[1].plot(time_array, T)
        axes[1].set_title("Échelle journalière (modèle 1)")
    else:
        axes[1].plot(time_array[:30*24], T[:30*24])
        axes[1].set_title("Échelle mensuelle (30 jours)")
    # Daily (24h)
    if model == 1:
        axes[2].plot(time_array, T)
        axes[2].set_title("Échelle journalière")
        axes[2].set_xlabel(f"Temps ({unit})")
    else:
        axes[2].plot(time_array[:24], T[:24])
        axes[2].set_title("Échelle journalière (premier jour)")
        axes[2].set_xlabel("Temps")
    for ax in axes:
        ax.set_ylabel("Température (K)")
        ax.grid(True)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf

# ---------- Nouvelle route -------------------
@app.route("/multi_zoom")
def multi_zoom():
    model = int(request.args.get("model", 1))
    lat   = float(request.args.get("lat", 48.85))
    lon   = float(request.args.get("lon", 2.35))
    buf = graphiques_multi_zoom(model, lat, lon)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
