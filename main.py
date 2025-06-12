from flask import Flask, send_file, request
import matplotlib.pyplot as plt
import numpy as np
import io

app = Flask(__name__)

def temp(P_recu):
    c = 2.25e5
    S = 1
    T0 = 273
    sigma = 5.67e-8
    dt = 3600
    A = 0.3
    T = [T0]
    for i in range(len(P_recu) - 1):
        flux_sortant = 0.5 * sigma * S * (T[i])**4
        T_apres = T[i] + dt * ((1 - A) * P_recu[i] * S - flux_sortant) / c
        T.append(T_apres)
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
        puissance = max(0, S0 * prod)
        puissances.append(puissance)
    return puissances

def liste(l): return l * 10

@app.route("/run")
def run_simulation():
    lat = float(request.args.get("lat", 48.85))
    lon = float(request.args.get("lon", 2.35))
    jour = int(request.args.get("jour", 172))
    puissances = liste(puissance_recue_par_heure(lat, lon, jour))
    temperatures = temp(puissances)

    plt.figure(figsize=(10, 4))
    plt.plot(range(len(temperatures)), temperatures)
    plt.xlabel("Heures")
    plt.ylabel("Température (K)")
    plt.title(f"Température simulée - lat: {lat}, lon: {lon}, jour: {jour}")
    plt.grid()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)  # PORT imposé par Render
