# CREP — Visualisation interactive

Ce dépôt affiche des graphes de température dynamiques avec zoom (Chart.js) et renvoie les données via Flask.

## Déploiement rapide sur Render

1. Poussez ces fichiers sur GitHub.
2. Allez sur Render.com → New Web Service.
3. Sélectionnez votre repo, Render détecte `render.yaml`.
4. Une fois déployé, accédez à `https://<votre-service>.onrender.com`.

⚠️ Si vous servez les pages HTML ailleurs (GitHub Pages, etc.),
mettez dans chaque `modeleX.html` :

```js
const API = 'https://<votre-service>.onrender.com';
```

pour pointer vers l’API Flask.
