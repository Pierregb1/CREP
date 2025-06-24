import matplotlib.pyplot as plt

taux_CO2 = []
annees = []

def calcul_CO2(annee):
    a = 1.9
    b = -3430
    if annee < 1952:# Valeur semble peu cohérente (ère industrielle à du commencer avant)
        return 278 #valeur moyenne avant ère industrielle
    else:
        return a * annee + b

for i in range(1740, 2050):
    annees.append(i)
    taux_CO2.append(calcul_CO2(i))

plt.plot(annees, taux_CO2)
plt.xlabel("Année")
plt.ylabel("Taux de CO₂ (ppm)")
plt.title("Évolution estimée du taux de CO₂ (modèle linéaire simplifié)")
plt.grid(True)
plt.show()