
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import io
import datetime
import math

app = Flask(__name__)

def create_plot(x, y, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    return fig

def compute_temperature_series(lat, lon, heat_capacity):
    S0 = 1361
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    incl = math.radians(23.5)
    sigma = 5.67e-8
    A = 0.3
    dt = 3600  # 1 h

    def daily_power(jour):
        decl = math.asin(math.sin(incl) * math.sin(2 * math.pi * (jour - 81) / 365))
        sun_vec = np.array([math.cos(decl), 0, math.sin(decl)])
        sun_vec /= np.linalg.norm(sun_vec)
        powers = []
        for h in range(24):
            angle = math.radians(15 * (h - 12))
            x = math.cos(lat_r) * math.cos(lon_r + angle)
            y = math.cos(lat_r) * math.sin(lon_r + angle)
            z = math.sin(lat_r)
            nrm = np.array([x, y, z])
            powers.append(max(0, S0 * np.dot(nrm, sun_vec)))
        return powers

    P = [p for j in range(1, 366) for p in daily_power(j)]
    T = [273]
    for p in P:
        flux_out = 0.5 * sigma * (T[-1] ** 4)
        T.append(T[-1] + dt * ((1 - A) * p - flux_out) / heat_capacity)
    times = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
    return times, T

@app.route("/run")
def run():
    model = int(request.args.get("model", 1))
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    window_days = int(request.args.get("days", 365))

    if model == 1:
        hours = np.linspace(0, 24, 1000)
        temp = 273 + 10 * np.exp(-hours / 5)
        if window_days == 1:
            x = hours[:int(1000 * 1 / 24)]
            y = temp[:int(1000 * 1 / 24)]
        elif window_days == 30:
            x = hours[:int(1000 * 12 / 24)]
            y = temp[:int(1000 * 12 / 24)]
        else:
            x = hours
            y = temp
        fig = create_plot(x, y, "Modèle 1 : Refroidissement", "Temps (h)", "T (K)")

    elif model in [2, 3, 4]:
        heat_capacity = {2: 2.25e5, 3: 1.5e5, 4: 3e5}[model]
        x, y = compute_temperature_series(lat, lon, heat_capacity)
        n = len(x)
        points_per_day = 24
        window_points = min(int(window_days * points_per_day), len(x))
        x = x[:window_points]
        y = y[:window_points]
        fig = create_plot(x, y, f"Modèle {model} — {window_days} jours", "Temps", "T (K)")

    else:
        return "Modèle inconnu", 400

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
