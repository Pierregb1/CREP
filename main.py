from flask import Flask, request, send_file, jsonify
import matplotlib.pyplot as plt
import numpy as np
import datetime
import math
import io

app = Flask(__name__)

@app.route("/data")
def get_model_data():
    model = int(request.args.get("model", 1))
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    zoomX = float(request.args.get("zoomX", 1.0))

    if model == 1:
        time_max = 24 / zoomX
        x = np.linspace(0, time_max, 1000)
        y = 273 + 10 * np.exp(-x / 5)
        return jsonify({"x": list(x), "y": list(y)})

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

    P = annee(chaque_jour(lat, lon))
    c_dict = {2: 2.25e5, 3: 1.5e5, 4: 3e5}
    T = temp(P, c_dict.get(model, 2.25e5))
    x = [(datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i)).strftime("%Y-%m-%d %H:%M") for i in range(len(T))]
    return jsonify({"x": x, "y": list(T)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
