
from flask import Flask, request, jsonify
import numpy as np, datetime, math, importlib.util, importlib, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Paths to user model files
FILE_MODEL2 = "Code_complet_V2.py"
FILE_MODEL3 = "Code_complet_V3_1.py"
FILE_MODEL4 = "modele 4 version api nasa.py"

app = Flask(__name__)

def simulate_model1(days):
    hours_total = 24
    x = np.linspace(0, hours_total, 1000)
    y = 273 + 10*np.exp(-x/5)
    if days<=1:
        # scale hours to proportion of day
        length = int(1000*days/hours_total)
        x = x[:length]
        y = y[:length]
    return x.tolist(), y.tolist()

def load_module_from_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # fermer toutes figures éventuelles créées à l'import
    plt.close('all')
    return mod

def simulate_with_user_module(path, lat, lon, days):
    mod = load_module_from_file(path, f"mod_{hash(path)}")
    P = mod.annee(mod.chaque_jour(lat, lon))
    # Tronquer P à days*24 points
    n_points = min(len(P), days*24)
    P = P[:n_points]
    T = mod.temp(P)
    # Dates
    dates = [datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
    dates = dates[:n_points]
    return [d.isoformat() for d in dates], T[:n_points]

@app.route("/data")
def data():
    model = int(request.args.get("model",1))
    lat   = float(request.args.get("lat", 48.85))
    lon   = float(request.args.get("lon", 2.35))
    days  = int(request.args.get("days",365))
    days = max(1, min(days, 365)) # clamp

    if model==1:
        x,y = simulate_model1(days)
    elif model==2:
        x,y = simulate_with_user_module(FILE_MODEL2, lat, lon, days)
    elif model==3:
        x,y = simulate_with_user_module(FILE_MODEL3, lat, lon, days)
    elif model==4:
        try:
            x,y = simulate_with_user_module(FILE_MODEL4, lat, lon, days)
        except Exception as e:
            return jsonify({'error':'Model 4 failed','details':str(e)}),500
    else:
        return jsonify({'error':'Model not found'}),404

    return jsonify({'x':x,'y':y})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
