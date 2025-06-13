from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

# Création silencieuse de la carte pour les polygones de terre
fig, ax = plt.subplots()
m = Basemap(projection='cyl', resolution='l', ax=ax)
m.drawcoastlines()

# Extraction des polygones terrestres
shapely_land_polygons = []
for poly in m.landpolygons:
    coords = poly.get_coords()
    shapely_land_polygons.append(Polygon(coords))

def classify_point(lon, lat):
    """Renvoie la capacité thermique massique (int)"""
    if abs(lat) > 75:
        return 2060  # Glace
    point = Point(lon, lat)
    if any(polygon.contains(point) for polygon in shapely_land_polygons):
        return 1046  # Terre
    else:
        return 4180  # Mer

def masse_volumique_point(lon, lat):
    """Renvoie la masse volumique (int) en kg/m³"""
    if abs(lat) > 75:
        return 917  # Glace
    point = Point(lon, lat)
    if any(polygon.contains(point) for polygon in shapely_land_polygons):
        return 2600  # Terre
    else:
        return 1000  # Mer

def analyser_point_manuellement(lat, lon):
    """Renvoie uniquement la capacité thermique massique"""
    return classify_point(lon, lat)

# Exemple d'utilisation (à réutiliser ou commenter selon le besoin)
while True:
    try:
        lat_input = input("\nEntrer la latitude (ou 'q' pour quitter) : ")
        if lat_input.lower() == 'q':
            break
        lat = float(lat_input)
        lon = float(input("Entrer la longitude : "))

        cm = analyser_point_manuellement(lat, lon)
        rho = masse_volumique_point(lon, lat)

        print(cm)
        print(rho)

    except ValueError:
        break
