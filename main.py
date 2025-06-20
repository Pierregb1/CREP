
from flask import Flask, request, redirect, url_for, Response, send_from_directory
import subprocess, os, html

app = Flask(__name__)

SCRIPT_MAP = {
    "modele2": "scripts/modele2.py",
    "modele3": "scripts/modele3.py",
    "modele4": "scripts/modele4.py"
}

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

@app.route("/model/<model_name>", methods=["GET", "POST"])
def model_page(model_name):
    if model_name not in SCRIPT_MAP:
        return "Modèle inconnu", 404

    message = ""
    lat = request.values.get("lat", "")
    lon = request.values.get("lon", "")
    zoom = request.values.get("zoom", "annuel")

    if request.method == "POST":
        lat = request.form["lat"]
        lon = request.form["lon"]
        zoom = request.form["zoom"]
        # Run the script
        try:
            subprocess.run(
                ["python", SCRIPT_MAP[model_name], lat, lon, zoom],
                check=True
            )
            message = "Graphique mis à jour !"
        except subprocess.CalledProcessError as e:
            message = f"Erreur lors de la génération : {html.escape(str(e))}"

    # Construct HTML dynamically
    img_filename = f"{model_name}_graph_{zoom}.png"
    img_path = f"/static/{img_filename}" if os.path.exists(f"static/{img_filename}") else ""
    form_html = f'''
    <h1>{html.escape(model_name.capitalize())}</h1>
    <form method="post">
      <label>Latitude : <input type="number" step="any" name="lat" value="{html.escape(lat)}" required></label><br>
      <label>Longitude : <input type="number" step="any" name="lon" value="{html.escape(lon)}" required></label><br>
      <label>Zoom:
        <select name="zoom">
          <option value="annuel" {"selected" if zoom=="annuel" else ""}>Annuel</option>
          <option value="mensuel" {"selected" if zoom=="mensuel" else ""}>Mensuel</option>
          <option value="journalier" {"selected" if zoom=="journalier" else ""}>Journalier</option>
        </select>
      </label><br>
      <button type="submit">Générer</button>
    </form>
    <p>{html.escape(message)}</p>
    '''
    if img_path:
        form_html += f'<h2>Graphique ({zoom})</h2><img src="{img_path}" width="100%">'
    form_html += '<p><a href="/">Retour accueil</a></p>'
    return Response(form_html, mimetype="text/html")

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(host="0.0.0.0", port=10000)
