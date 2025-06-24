### Les chevreaux brillants


***
| Projet CREP |
|-----------------------------------------|

* <details>
  <summary>Comment se repérer dans nos fichiers ?</summary>
  Notre projet est divisé en plusieurs dossiers, représentant les différentes évolutions du modèle, numérotées de 1 à 6. Dans chacun de ces dossiers, vous trouverez un fichier pdf, résumant les avancées de ce modèle (par rapport aux versions précédentes), ainsi qu'un code Python associé. Il peut être nécessaire d'installer sur Python les librairies suivantes : numpy, matplotlib, datetime, math, request, shapely.geometry, mpl_toolkits.basemap.
  </details>

* <details>
  <summary>Nos différents modèles :</summary>
    
<kbd>[MODELE 1](https://github.com/Pierregb1/CREP/tree/main/Mod%C3%A8le%201)</kbd> On modélise la baisse de température la nuit via la loi de Newton, et le premier principe.    

<kbd>[MODELE 2](https://github.com/Pierregb1/CREP/tree/main/Mod%C3%A8le%202)</kbd> On calcule et représente l'évolution de la température en fonction du temps, grâce à la loi de Stefan.

<kbd>[MODELE 3](https://github.com/Pierregb1/CREP/tree/main/Mod%C3%A8le%203)</kbd> On tient compte de l'albédo qui varie en fonction de la latitude et de la longitude du point choisi. Pour cela on effectue des appels API.

<kbd>[MODELE 4](https://github.com/Pierregb1/CREP/tree/main/Mod%C3%A8le%204)</kbd> On a rajouté le calcul du coefficient de conducto-convexion, qui varie au cours du temps. 

<kbd>[MODELE 5](https://github.com/Pierregb1/CREP/tree/main/Mod%C3%A8le%205)</kbd> On tient ensuite compte de la variation de la capacité thermique, en fonction de latitude et longitude (séparation entre eau, glace et terre).

<kbd>[MODELE 6](https://github.com/Pierregb1/CREP/tree/main/Mod%C3%A8le%206)</kbd> On a tenu compte du coefficient alpha (quotient de la puissance absorbée par l'atmosphère sur la puissance émise par la Terre), qui varie selon la concentration en CO2 dans l'atmosphère.
</details>

* <details>
  <summary>Pistes pour l'année prochaine :</summary>
  Il est clair que certaines puissances cédées par la Terre, et non négligeables, n'ont pas été modélisées par notre groupe. Parmi ces dernières, on retrouve notamment l'évapo-transpiration : nous avons effectué des recherches mais nous ne les avons pas intégré dans le code. <kbd>[A retrouver ici](https://github.com/Pierregb1/CREP/blob/main/Pistes%20futures/Mode%CC%80le_e%CC%81vapotranspiration.pdf)</kbd>
</details>
