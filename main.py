
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import io
import modele1p

app = Flask(__name__)

@app.route("/run")
def run():
    model = int(request.args.get("model", 1))
    if model == 1:
        T = modele1p.temp()
        x = np.linspace(0, 24, len(T))
        fig, ax = plt.subplots()
        ax.plot(x, T)
        ax.set_title("Modèle 1 — Refroidissement simple")
        ax.set_xlabel("Temps (h)")
        ax.set_ylabel("Température (K)")
        ax.grid(True)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    else:
        return "Modèle non pris en charge", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
