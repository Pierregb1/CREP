from flask import Flask, request, send_file
import io
import matplotlib.pyplot as plt
import modele1p, modele2p, modele3p, modele4p, modele5p

app = Flask(__name__)

@app.route("/run")
def run():
    model = request.args.get("model", "1")
    lat = float(request.args.get("lat", "48.85"))
    lon = float(request.args.get("lon", "2.35"))

    if model == "1":
        T = modele1p.temp()
    elif model == "2":
        T = modele2p.temp(lat, lon)
    elif model == "3":
        T = modele3p.temp(lat, lon)
    elif model == "4":
        T = modele4p.temp(lat, lon)
    elif model == "5":
        T = modele5p.temp(lat, lon)
    else:
        return "Modèle inconnu", 400

    plt.figure(figsize=(10, 4))
    plt.plot(T)
    plt.title(f"Température - modèle {model}")
    plt.xlabel("Temps (h)")
    plt.ylabel("Température (K)")
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()
    return send_file(img, mimetype="image/png")
