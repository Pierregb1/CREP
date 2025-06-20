from flask import Flask, request, send_from_directory, redirect
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def accueil():
    return send_from_directory('.', 'index.html')

@app.route('/modele1')
def modele1():
    return send_from_directory('.', 'modele1.html')

@app.route('/modele2', methods=['GET', 'POST'])
def modele2():
    if request.method == 'POST':
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        subprocess.run(["python", "Code_complet_V2.py", lat, lon])
    return send_from_directory('.', 'modele2_form.html')

@app.route('/modele3', methods=['GET', 'POST'])
def modele3():
    if request.method == 'POST':
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        subprocess.run(["python", "Code_complet_V3_1.py", lat, lon])
    return send_from_directory('.', 'modele3_form.html')

@app.route('/modele4', methods=['GET', 'POST'])
def modele4():
    if request.method == 'POST':
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        subprocess.run(["python", "essai 2 v4.py", lat, lon])
    return send_from_directory('.', 'modele4_form.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/<path:filename>')
def fallback(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    os.makedirs("static", exist_ok=True)
    app.run(debug=False, host='0.0.0.0', port=10000)