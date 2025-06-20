
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import io
import datetime
import math

app = Flask(__name__)

# =================== Modèle 1 =================== #
def run_model1(zoomX):
    fig, ax = plt.subplots()
    time_max = 24 / zoomX
    x = np.linspace(0, time_max, 1000)
    y = 273 + 10 * np.exp(-x / 5)
    ax.plot(x, y)

    ax.set_title("Modèle 1 : Refroidissement")
    ax.set_xlabel("Temps (heures)")
    ax.set_ylabel("Température (K)")
    ax.grid(True)
    return fig

# =================== Fonctions auxiliaires communes =================== #
def puissance_jour(lat_deg, lon_deg, jour):
    """Flux horaire reçu sur une journée (24 valeurs)"""
    S0 = 1361  # constante solaire W/m²
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    inclinaison = math.radians(23.5)
    declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2 * math.pi * (jour - 81) / 365))
    # direction vecteur Soleil (approx)
    soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
    soleil /= np.linalg.norm(soleil)
    puissances = []
    for h in range(24):
        angle = math.radians(15 * (h - 12))  # angle horaire
        x = np.cos(lat) * np.cos(lon + angle)
        y = np.cos(lat) * np.sin(lon + angle)
        z = np.sin(lat)
        normale = np.array([x, y, z])
        puissances.append(max(0, S0 * np.dot(normale, soleil)))
    return puissances

def sequence_annee(lat, lon):
    """Retourne la liste des 8760 flux horaires pour l'année"""
    return [val for jour in range(1, 366) for val in puissance_jour(lat, lon, jour)]

def temperature_evolution(P_recu, c):
    S = 1          # surface élémentaire m²
    T0 = 273       # K
    sigma = 5.67e-8
    dt = 3600      # pas 1 h
    A = 0.3        # albédo
    T = [T0]
    for p in P_recu:
        flux_sortant = 0.5 * sigma * S * (T[-1] ** 4)
        T.append(T[-1] + dt * ((1 - A) * p * S - flux_sortant) / c)
    return T[1:]  # on enlève T0 initial

# =================== Modèle 2 et 4 identiques à avant (omises pour concision) =================== #

# =================== Modèle 3 – 3 ZOOMS =================== #
def run_model3(lat, lon):
    """Retourne une figure avec 3 sous‑graphes : annuel, mensuel, journalier."""
    P = sequence_annee(lat, lon)
    T = temperature_evolution(P, c=1.5e5)
    dates = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]

    # Indices pour découper
    jour_heures = 24
    mois_heures = 31 * 24  # janvier

    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharey=True)

    # Annuel
    axes[0].plot(dates, T)
    axes[0].set_title("Température annuelle")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("T (K)")
    axes[0].grid(True)

    # Mensuel : janvier
    axes[1].plot(dates[:mois_heures], T[:mois_heures], color='tab:orange')
    axes[1].set_title("Température – janvier")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("T (K)")
    axes[1].grid(True)

    # Journalier : 1ᵉʳ janvier
    axes[2].plot(dates[:jour_heures], T[:jour_heures], color='tab:green')
    axes[2].set_title("Température – 1ᵉʳ janvier")
    axes[2].set_xlabel("Temps")
    axes[2].set_ylabel("T (K)")
    axes[2].grid(True)

    fig.suptitle(f"Modèle 3 – Lat {lat:.2f}°, Lon {lon:.2f}°", fontsize=14)
    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    return fig

# =================== Modèle 2 =================== #
def run_model2(lat, lon):
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

    def temp(P_recu):
        c = 2.25e5
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

    P = annee(chaque_jour(lat, lon))
    T = temp(P)
    dates = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
    fig, ax = plt.subplots()
    ax.plot(dates, T)
    ax.set_title("Modèle 2 — Température annuelle")
    ax.set_xlabel("Temps")
    ax.set_ylabel("Température (K)")
    ax.grid(True)
    return fig

# =================== Modèle 4 =================== #
def run_model4(lat, lon):
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

    def temp(P_recu):
        c = 3e5
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

    P = annee(chaque_jour(lat, lon))
    T = temp(P)
    dates = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
    fig, ax = plt.subplots()
    ax.plot(dates, T)
    ax.set_title("Modèle 4 — Température annuelle")
    ax.set_xlabel("Temps")
    ax.set_ylabel("Température (K)")
    ax.grid(True)
    return fig


# =================== API Route =================== #
@app.route("/run")
def run():
    model = int(request.args.get("model", 1))
    zoomX = float(request.args.get("zoomX", 1.0))
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))

    if model == 1:
        fig = run_model1(zoomX)
    elif model == 2:
        fig = run_model2(lat, lon)
    elif model == 3:
        fig = run_model3(lat, lon)
    elif model == 4:
        fig = run_model4(lat, lon)
    else:
        return "Modèle inconnu", 400

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
