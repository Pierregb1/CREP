
from flask import Flask, request, send_file, jsonify
import matplotlib.pyplot as plt
import numpy as np
import datetime
import math
import io
import base64

app = Flask(__name__)

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

@app.route("/data_model2")
def data_model2():
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    P = annee(chaque_jour(lat, lon))
    T = temp(P, 2.25e5)
    dates = [(datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i)).isoformat() for i in range(len(T))]
    return jsonify({"x": dates, "y": T})

@app.route("/multi_zoom_base64")
def multi_zoom_base64():
    model = int(request.args.get("model", 1))
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    fig, axs = plt.subplots(3, 1, figsize=(10, 12))

    if model == 1:
        x = np.linspace(0, 24, 1000)
        y = 273 + 10 * np.exp(-x / 5)
        axs[0].plot(x, y)
        axs[1].plot(x, y)
        axs[2].plot(x, y)
    else:
        c_map = {2: 2.25e5, 3: 1.5e5, 4: 3e5}
        P = annee(chaque_jour(lat, lon))
        T = temp(P, c_map.get(model, 2.25e5))
        dates = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
        axs[0].plot(dates, T)
        axs[1].plot(dates[:30*24], T[:30*24])
        axs[2].plot(dates[:24], T[:24])

    titles = ["Zoom annuel", "Zoom mensuel", "Zoom journalier"]
    for ax, title in zip(axs, titles):
        ax.set_title(title)
        ax.set_xlabel("Temps")
        ax.set_ylabel("Température (K)")
        ax.grid(True)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return {"img": f"data:image/png;base64,{img_base64}"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
