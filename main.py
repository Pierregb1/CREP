from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime
import io

app = Flask(__name__)

def temp(P_recu):
    c = 2.25e5
    S = 1
    T0 = 283
    sigma = 5.67e-8
    dt = 3600
    A = 0.3
    h = 10
    T_air = 283
    T = [T0]
    for i in range(len(P_recu)):
        flux_entrant = (1 - A) * P_recu[i] * S
        flux_sortant_rad = 0.5 * sigma * S * T[i]**4
        flux_convection = h * S * (T[i] - T_air)
        dT = dt * (flux_entrant - flux_sortant_rad - flux_convection) / c
        T.append(T[i] + dT)
    return T

def puissance_recue_par_heure(latitude_deg, longitude_deg, jour_de_l_annee):
    S0 = 1361
    lat = np.radians(latitude_deg)
    lon = np.radians(longitude_deg)
    inclinaison = np.radians(23.5)
    declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2 * np.pi * (jour_de_l_annee - 81) / 365))
    soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
    soleil /= np.linalg.norm(soleil)

    puissances = []
    for h in range(24):
        angle_terre = np.radians(15 * (h - 12))
        x = np.cos(lat) * np.cos(lon + angle_terre)
        y = np.cos(lat) * np.sin(lon + angle_terre)
        z = np.sin(lat)
        normale = np.array([x, y, z])
        prod = np.dot(normale, soleil)
        puissances.append(max(0, S0 * prod))
    return puissances

def chaque_jour(lat, lon):
    return [puissance_recue_par_heure(lat, lon, j) for j in range(1, 366)]

def annee(p_jour):
    return [val for jour in p_jour for val in jour]

@app.route("/run")
def run():
    # Paramètres reçus dans l’URL
    try:
        lat = float(request.args.get("lat", 48.85))
        lon = float(request.args.get("lon", 2.35))
    except:
        lat, lon = 48.85, 2.35

    # Simulation
    puissances = annee(chaque_jour(lat, lon))
    temperatures = temp(puissances)
    date_debut = datetime.datetime(2024, 1, 1)
    dates = [date_debut + datetime.timedelta(hours=i) for i in range(len(temperatures))]

    # Graphique
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(dates, temperatures)
    ax.set_xlabel("Date")
    ax.set_ylabel("Température (K)")
    ax.set_title(f"Température sur l'année à lat {lat}°, lon {lon}°")
    ax.grid(True)

    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    plt.tight_layout()

    # Sauvegarde en mémoire
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

app.run(host="0.0.0.0", port=10000)  # Pour Render
