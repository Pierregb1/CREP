from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import datetime
import math

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Autorise n'importe quelle origine (GitHub Pages → Render)

@app.route('/')
def home():
    # Sert index.html
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    # Sert n'importe quel fichier statique (HTML, JS, CSS…)
    return send_from_directory('.', filename)

@app.route("/data")
def get_model_data():
    """Retourne les données JSON pour un modèle.

    Paramètres query :
      - model (int) : 1,2,3,4
      - lat, lon (float) : latitude, longitude (modèles 2‑4)
      - zoomX (float) : facteur de zoom (modèle 1)
    """
    model = int(request.args.get("model", 1))
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    zoomX = float(request.args.get("zoomX", 1.0))

    # Modèle 1 : décroissance exponentielle sur 24 h, avec zoom
    if model == 1:
        time_max = 24 / zoomX
        x = np.linspace(0, time_max, 1000)
        y = 273 + 10 * np.exp(-x / 5)
        return jsonify({"x": x.tolist(), "y": y.tolist()})

    # Fonctions communes aux modèles 2–4
    def puissance(lat_deg, lon_deg, jour):
        S0 = 1361
        lat = math.radians(lat_deg)
        lon = math.radians(lon_deg)
        inclinaison = math.radians(23.5)
        declinaison = math.asin(math.sin(inclinaison) * math.sin(2 * math.pi * (jour - 81) / 365))
        soleil = np.array([math.cos(declinaison), 0, math.sin(declinaison)])
        soleil = soleil / np.linalg.norm(soleil)
        puissances = []
        for h in range(24):
            angle = math.radians(15 * (h - 12))
            x = math.cos(lat) * math.cos(lon + angle)
            y = math.cos(lat) * math.sin(lon + angle)
            z = math.sin(lat)
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

    c_dict = {2: 2.25e5, 3: 1.5e5, 4: 3e5}
    if model in c_dict:
        P = annee(chaque_jour(lat, lon))
        T = temp(P, c_dict[model])
        x_dates = [(datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i)).strftime("%Y-%m-%d %H:%M")
                   for i in range(len(T))]
        return jsonify({"x": x_dates, "y": T})

    # Modèle non reconnu
    return jsonify({"error": "Modèle inconnu"}), 400


if __name__ == "__main__":
    # Render définira $PORT automatiquement
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
