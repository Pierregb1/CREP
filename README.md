# CREP — Visualisation interactive de la température terrestre

Ce dépôt permet d’afficher dynamiquement des modèles de température avec zoom sur les abscisses via Chart.js et Flask.

## Structure
- `main.py` : serveur Flask avec API `/data`
- `index.html`, `modele1.html` à `modele4.html` : pages interactives
- `requirements.txt` : dépendances Python
- `render.yaml` : configuration Render.com

## Déploiement sur Render
1. Crée un dépôt GitHub avec tous ces fichiers.
2. Connecte ton compte à [https://render.com](https://render.com)
3. Clique sur "New Web Service" > choisis ton dépôt
4. Render détectera `render.yaml` et configurera le service automatiquement
5. Accède à `https://<ton-service>.onrender.com`

