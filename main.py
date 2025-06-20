
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

def call_function_adaptively(fn, *args):
    """Appelle fn avec un nombre d'arguments correspondant à sa signature."""
    sig = inspect.signature(fn)
    params = [p for p in sig.parameters.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    needed = len([p for p in params if p.default is inspect._empty])
    # slice args pour respecter needed
    return fn(*args[:needed])

def load_temperature(module_name, lat=None, lon=None, zoomX=None):
    mod = importlib.import_module(module_name)
    for name in ("temp", "run", "simulate", "compute", "temperature"):
        fn = getattr(mod, name, None)
        if callable(fn):
            # Essayer d'appeler avec différents combos
            try:
                if zoomX is not None:
                    return call_function_adaptively(fn, zoomX)
                else:
                    return call_function_adaptively(fn, lat, lon)
            except Exception as e:
                last_exc = e
    raise RuntimeError(f"Impossible d'appeler une fonction temp-like dans {module_name}: {last_exc}")

def run_model1():
    try:
        T = load_temperature("modele1p", zoomX=zoomX)
        if not isinstance(T, (list, np.ndarray)):
            raise ValueError("modele1p.temp doit renvoyer une liste/ndarray")
        x = np.linspace(0, 24/zoomX, len(T))
        fig, ax = plt.subplots(); ax.plot(x, T)
        ax.set_title("Modèle 1"); ax.set_xlabel("Heure"); ax.set_ylabel("T (K)"); ax.grid(True)
        return fig
    except Exception as e:
        fig, ax = plt.subplots(); ax.text(0.5,0.5,str(e),ha='center',va='center'); ax.axis('off'); return fig

def run_generic(model, lat, lon):
    module_name = f"modele{model}p"
    try:
        T = load_temperature(module_name, lat, lon)
        # si retourne tuple (dates, T) déjà
        if isinstance(T, tuple) and len(T) == 2:
            dates, temp = T
            return compose_triple_view(dates, temp, f"Modèle {model}")
        if len(T) == 8761:
            T = T[1:]
        dates = [datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
        return compose_triple_view(dates, T, f"Modèle {model}")
    except Exception as e:
        fig, ax = plt.subplots(); ax.text(0.5,0.5,str(e),ha='center',va='center'); ax.axis('off'); return fig

@app.route("/run")
def run():
    model = int(request.args.get("model",1))
    lat   = float(request.args.get("lat",48.85))
    lon   = float(request.args.get("lon",2.35))
    zoomX = float(request.args.get("zoomX",1.0))
    if model == 1:
        fig = run_model1(zoomX)
    elif model in (2,3,4,5):
        fig = run_generic(model, lat, lon)
    else:
        return "Modèle inconnu", 400
    buf=io.BytesIO(); fig.savefig(buf,format="png"); buf.seek(0)
    return send_file(buf,mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)
