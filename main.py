from flask import Flask, request, send_file
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Génération de dates

def generate_dates(period='year'):
    today = datetime.today()
    if period == 'year':
        start = today - timedelta(days=365)
    elif period == 'month':
        start = today - timedelta(days=30)
    elif period == 'day':
        start = today - timedelta(days=1)
    dates = [start + i * (today - start) / 100 for i in range(101)]
    return dates

# Fonctions de simulation pour chaque modèle

def run_model1(lat, lon):
    # Simulation basique : sinusoïde
    dates = generate_dates('year')
    T = [20 + 5 * np.sin(2 * np.pi * i / len(dates)) for i, _ in enumerate(dates)]
    return dates, T

def run_model2(lat, lon):
    dates = generate_dates('month')
    T = [15 + 3 * np.sin(4 * np.pi * i / len(dates)) for i, _ in enumerate(dates)]
    fig, ax = plt.subplots()
    ax.plot(dates, T)
    return fig

def run_model3(lat, lon):
    dates = generate_dates('day')
    T = [10 + 2 * np.sin(8 * np.pi * i / len(dates)) for i, _ in enumerate(dates)]
    fig, ax = plt.subplots()
    ax.plot(dates, T)
    return fig

def run_model4(lat, lon):
    dates = generate_dates('year')
    T = [25 + 7 * np.sin(1 * np.pi * i / len(dates)) for i, _ in enumerate(dates)]
    fig, ax = plt.subplots()
    ax.plot(dates, T)
    return fig

# Route principale

@app.route('/run')
def run():
    model = int(request.args.get('model', 1))
    lat = float(request.args.get('lat', 0))
    lon = float(request.args.get('lon', 0))

    if model == 1:
        dates, T = run_model1(lat, lon)
        # Retourne JSON ou autre selon modèle 1
        return {'dates': [d.isoformat() for d in dates], 'T': T}
    elif model == 2:
        fig = run_model2(lat, lon)
    elif model == 3:
        fig = run_model3(lat, lon)
    elif model == 4:
        fig = run_model4(lat, lon)
    else:
        return {'error': 'Modèle inconnu'}, 400

    # Génération de l'image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
