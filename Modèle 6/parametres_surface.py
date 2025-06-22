# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 14:39:51 2025

@author: jeann
"""
from shapely.geometry import Point, Polygon
from mpl_toolkits.basemap import Basemap
from matplotlib.figure import Figure
import requests

# Création silencieuse de la carte pour les polygones de terre
fig = Figure()  # Crée une figure sans interface
ax = fig.add_subplot(111)
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

# ---------------------- API NASA POWER pour l’albédo ---------------------- #
def get_mean_albedo(lat, lon, start="20220101", end="20231231"):
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        allsky = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        upsky = data['properties']['parameter']['ALLSKY_SFC_SW_UP']

        albedo_values = [
            upsky[day] / allsky[day]
            for day in allsky if allsky[day] > 0 and upsky[day] is not None
        ]
        return sum(albedo_values) / len(albedo_values) if albedo_values else 0.3
    except Exception as e:
        print("Erreur lors de la récupération de l'albédo :", e)
        return 0.3