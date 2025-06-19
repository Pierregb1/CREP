
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import io
import datetime
import math

app = Flask(__name__)

def slice_series_by_days(x, y, window_days=365, offset_frac=0.0, points_per_day=24):
    """Return a slice of the series covering `window_days` starting at the given offset fraction (0–1)."""
    n = len(x)
    total_days = n / points_per_day
    window_days = max(1, min(window_days, total_days))  # clamp
    window_points = int(window_days * points_per_day)
    max_start = n - window_points
    start_idx = int(offset_frac * max_start)
    end_idx = start_idx + window_points
    return x[start_idx:end_idx], y[start_idx:end_idx]

def create_plot(x, y, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    return fig

# ------------------- MODEL 1 ------------------- #
def run_model1(window_hours=24, offset_frac=0.0):
    hours = np.linspace(0, 24, 1000)
    temp = 273 + 10 * np.exp(-hours / 5)

    # Convert hours to fraction of day for slicing
    points_per_hour = len(hours) / 24
    window_points = int(max(1, window_hours * points_per_hour))
    max_start = len(hours) - window_points
    start_idx = int(offset_frac * max_start)
    end_idx = start_idx + window_points

    x_slice = hours[start_idx:end_idx]
    y_slice = temp[start_idx:end_idx]

    return create_plot(x_slice, y_slice, "Modèle 1 : Refroidissement", "Temps (heures)", "Température (K)")

# Utility to compute temperatures (shared)
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

def run_model_generic(lat, lon, c, window_days=365, offset_frac=0.0, title="Modèle"):
    x, y = compute_temperature_series(lat, lon, c)
    x_slice, y_slice = slice_series_by_days(x, y, window_days, offset_frac, 24)
    return create_plot(x_slice, y_slice, title, "Temps", "Température (K)")

@app.route("/run")
def run():
    model = int(request.args.get("model", 1))
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    window = float(request.args.get("window", 365))  # days for models 2-4, hours for model1
    offset = float(request.args.get("offset", 0.0))  # fraction 0–1

    if model == 1:
        fig = run_model1(window_hours=min(max(window, 1), 24), offset_frac=offset)
    elif model == 2:
        fig = run_model_generic(lat, lon, 2.25e5, window, offset, "Modèle 2 — Température annuelle (c = 2.25e5)")
    elif model == 3:
        fig = run_model_generic(lat, lon, 1.5e5, window, offset, "Modèle 3 — Température annuelle (c = 1.5e5)")
    elif model == 4:
        fig = run_model_generic(lat, lon, 3e5, window, offset, "Modèle 4 — Température annuelle (c = 3e5)")
    else:
        return "Modèle inconnu", 400

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
