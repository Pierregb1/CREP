import matplotlib.pyplot as plt

# Listes pour stocker les données
taux_CO2 = []
annees = []



def calcul_CO2(annee):
    a = 1.9
    b = -3430

    if 1838 <= annee <= 1972 :
        return 0.294* annee -262
    elif annee < 1952:
        return 278  # valeur moyenne avant ère industrielle
    else:
        return a * annee + b  # modèle linéaire

# Génération des données de 1740 à 2050
for i in range(1740, 2050):
    annees.append(i)
    taux_CO2.append(calcul_CO2(i))

# Tracé du graphique
plt.plot(annees, taux_CO2, label="CO₂ (ppm)")
plt.xlabel("Année")
plt.ylabel("Taux de CO₂ (ppm)")
plt.title("Évolution estimée du taux de CO₂")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
