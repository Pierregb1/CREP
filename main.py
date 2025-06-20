
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import importlib, inspect, io, datetime

app = Flask(__name__)

def compose_triple_view(dates, T, title):
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharey=True)
    axes[0].plot(dates, T); axes[0].set_title(f"{title} — annuel"); axes[0].grid(True)
    axes[1].plot(dates[:31*24], T[:31*24], color='tab:orange'); axes[1].set_title("Janvier"); axes[1].grid(True)
    axes[2].plot(dates[:24], T[:24], color='tab:green'); axes[2].set_title("1ᵉʳ janvier"); axes[2].set_xlabel("Heure"); axes[2].grid(True)
    fig.tight_layout(); return fig

def get_temperature(module_name, lat, lon):
    mod = importlib.import_module(module_name)
    for fn_name in ("temp", "run", "simulate", "compute", "temperature"):
        fn = getattr(mod, fn_name, None)
        if callable(fn):
            try:
                return fn(lat, lon)
            except TypeError:
                return fn()
    raise AttributeError(f"No temp-like function in {module_name}")

def run_model1(zoomX):
    fig, ax = plt.subplots(); x = np.linspace(0, 24/zoomX, 1000); ax.plot(x, 273+10*np.exp(-x/5))
    ax.set_title("Modèle 1"); ax.set_xlabel("Heure"); ax.set_ylabel("T (K)"); ax.grid(True); return fig

def run_generic(n, lat, lon):
    module_name = f"modele{n}p"
    try:
        T = get_temperature(module_name, lat, lon)
    except Exception as e:
        fig, ax = plt.subplots(); ax.text(0.5,0.5,str(e),ha='center',va='center'); ax.axis('off'); return fig
    if len(T)==8761: T=T[1:]
    dates=[datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
    return compose_triple_view(dates, T, f"Modèle {n}")

@app.route("/run")
def run():
    model = int(request.args.get("model",1))
    lat = float(request.args.get("lat",48.85)); lon=float(request.args.get("lon",2.35))
    zoomX=float(request.args.get("zoomX",1.0))
    if model==1: fig = run_model1(zoomX)
    elif model in (2,3,4,5): fig = run_generic(model, lat, lon)
    else: return "Modèle inconnu",400
    buf = io.BytesIO(); fig.savefig(buf,format="png"); buf.seek(0); return send_file(buf,mimetype="image/png")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
