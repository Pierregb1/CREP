from mpl_toolkits.basemap import Basemap
import numpy as np

# Exemple de code minimal pour tracer une carte

def plot_map():
    # Création d'une carte centrée
    m = Basemap(projection='merc', llcrnrlat=-80, urcrnrlat=80,
                llcrnrlon=-180, urcrnrlon=180, lat_ts=20, resolution='c')
    m.drawcoastlines()

    # Exemple de données aléatoires
    lons = np.linspace(-180, 180, 30)
    lats = np.linspace(-80, 80, 20)
    data = np.random.rand(len(lats), len(lons))

    # Transformation des coordonnées
    x, y = np.meshgrid(lons, lats)
    xi, yi = m(x, y)

    # Tracé des données
    cs = m.contourf(xi, yi, data)

    # Affichage
    print(cs)

if __name__ == "__main__":
    plot_map()
