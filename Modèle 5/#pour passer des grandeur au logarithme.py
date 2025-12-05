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
        return 278 # valeur moyenne avant ère industrielle
    else:
        return a * annee + b # modèle linéaire
 

for i in range(1740, 2050):
    annees.append(i)
    taux_CO2.append(calcul_CO2(i))

def concentration_CO2(annee):
    """
    Renvoie la concentration estimée de CO₂ en ppm pour une année donnée.
    """
    if 1838 <= annee <= 1972:
        return 0.294 * annee - 262
    elif annee < 1952:
        return 278  # valeur moyenne avant l'ère industrielle
    else:
        return 1.9 * annee - 3430  # modèle linéaire post-1952
print(concentration_CO2(2005))
# Tracé du graphique
plt.plot(annees, taux_CO2, label="CO₂ (ppm)")
plt.xlabel("Année")
plt.ylabel("Taux de CO₂ (ppm)")
plt.title("Évolution estimée du taux de CO₂")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
