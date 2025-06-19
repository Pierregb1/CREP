
# Même code que précédemment pour classify_point / masse_volumique_point
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
m = Basemap(projection='cyl', resolution='l', ax=ax)
m.drawcoastlines()
shapely_land_polygons = [Polygon(poly.get_coords()) for poly in m.landpolygons]

def classify_point(lon, lat):
    if abs(lat) > 75:
        return 2060
    point = Point(lon, lat)
    return 1046 if any(p.contains(point) for p in shapely_land_polygons) else 4180

def masse_volumique_point(lon, lat):
    if abs(lat) > 75:
        return 917
    point = Point(lon, lat)
    return 2600 if any(p.contains(point) for p in shapely_land_polygons) else 1000
