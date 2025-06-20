
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import importlib, inspect, numpy as np, datetime, io

app = Flask(__name__)

# -----------------------------------------------------------
# Helper : triple graphique (annuel / janvier / 1er janvier)
# -----------------------------------------------------------
def triple_view(dates, T, title):
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharey=True)
    axes[0].plot(dates, T); axes[0].set_title(f"{title} — annuel"); axes[0].grid(True)
    axes[1].plot(dates[:31*24], T[:31*24], color='tab:orange'); axes[1].set_title("Janvier"); axes[1].grid(True)
    axes[2].plot(dates[:24], T[:24], color='tab:green'); axes[2].set_title("1ᵉʳ janvier"); axes[2].set_xlabel("Heure"); axes[2].grid(True)
    fig.tight_layout(); return fig

# -----------------------------------------------------------
# Dynamic loader
# -----------------------------------------------------------
def load_temp(module_name, *args):
    mod = importlib.import_module(module_name)
    for fn_name in ("temp", "run", "simulate", "compute", "temperature"):
        fn = getattr(mod, fn_name, None)
        if callable(fn):
            return fn(*args) if args else fn()
    raise AttributeError(f"Pas de fonction temp-like dans {module_name}")

# ----------------- Modèle 1 (à zoom) -----------------------
def run_model1(zoomX):
    try:
        T = load_temp("modele1p_fixed", zoomX)
        x = np.linspace(0, 24/zoomX, len(T))
        fig, ax = plt.subplots(); ax.plot(x, T)
        ax.set_title("Modèle 1 — Refroidissement"); ax.set_xlabel("Heure"); ax.set_ylabel("T (K)"); ax.grid(True)
        return fig
    except Exception as e:
        fig, ax = plt.subplots(); ax.text(0.5,0.5,str(e),ha='center',va='center'); ax.axis('off'); return fig

# ----------------- Modèles 2 à 5 ---------------------------
def run_generic(model_num, lat, lon):
    module_name = f"modele{model_num}p"
    try:
        T = load_temp(module_name, lat, lon)
        if len(T) == 8761:  # certains modules gardent T0 initial
            T = T[1:]
        dates = [datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
        return triple_view(dates, T, f"Modèle {model_num}")
    except Exception as e:
        fig, ax = plt.subplots(); ax.text(0.5,0.5,str(e),ha='center',va='center'); ax.axis('off'); return fig

# ------------------ ROUTE API ------------------------------
@app.route("/run")
def run():
    model = int(request.args.get("model", 1))
    lat   = float(request.args.get("lat", 48.85))
    lon   = float(request.args.get("lon", 2.35))
    zoomX = float(request.args.get("zoomX",1.0))

    if model == 1:
        fig = run_model1(zoomX)
    elif model in (2,3,4,5):
        fig = run_generic(model, lat, lon)
    else:
        return "Modèle inconnu", 400

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
