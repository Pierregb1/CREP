
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import io, importlib, datetime
import sys
import traceback

app = Flask(__name__)  # Indispensable pour gunicorn

def load_temp(module_name, *args):
    try:
        mod = importlib.import_module(module_name)
    except Exception as e:
        print(f"Erreur import {module_name} : {e}", file=sys.stderr)
        raise
    for fn_name in ("temp", "run", "simulate", "compute", "temperature"):
        fn = getattr(mod, fn_name, None)
        if callable(fn):
            return fn(*args)
    raise AttributeError(f"Aucune fonction temp-like trouvée dans {module_name}")

def triple_view(dates, T, title):
    fig, ax = plt.subplots(3, 1, figsize=(10, 12), sharey=True)
    ax[0].plot(dates, T); ax[0].set_title(f"{title} — année"); ax[0].grid(True)
    ax[1].plot(dates[:31*24], T[:31*24]); ax[1].set_title("Janvier"); ax[1].grid(True)
    ax[2].plot(dates[:24], T[:24]); ax[2].set_title("1ᵉʳ janvier"); ax[2].set_xlabel("Heure"); ax[2].grid(True)
    fig.tight_layout()
    return fig

@app.route("/run")
def run():
    try:
        model = int(request.args.get("model", 1))
        lat = float(request.args.get("lat", 48.85))
        lon = float(request.args.get("lon", 2.35))
        year = int(request.args.get("year", 2024))

        if model == 1:
            T = load_temp("modele1p")  # Aucun argument
            x = np.arange(len(T))
            fig, ax = plt.subplots()
            ax.plot(x, T)
            ax.set_title("Modèle 1 — Refroidissement simple")
            ax.set_xlabel("Temps (pas)"); ax.set_ylabel("Température"); ax.grid(True)

        elif model in (2, 3, 4):
            T = load_temp(f"modele{model}p", lat, lon)
            if len(T) == 8761:  # On enlève la première valeur T0 si elle est redondante
                T = T[1:]
            dates = [datetime.datetime(2024, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
            fig = triple_view(dates, T, f"Modèle {model}")

        elif model == 5:
            T = load_temp("modele5p", lat, lon, year)
            dates = [datetime.datetime(year, 1, 1) + datetime.timedelta(hours=i) for i in range(len(T))]
            fig = triple_view(dates, T, "Modèle 5")

        else:
            return "Modèle inconnu", 400

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        print(traceback.format_exc())
        return f"Erreur : {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
