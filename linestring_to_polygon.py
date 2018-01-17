from fastkml import kml
from shapely.geometry import Point, LineString, Polygon, mapping

f = open('/tmp/andhra_pradesh.kml', 'r')
doc = f.read()

k = kml.KML()
k.from_string(doc)
features = list(k.features())

points = []
for f in list(features[0].features()):
	coords = [c[:-1] for c in f.geometry.coords[:]]
	points = points+coords

print mapping(Polygon(points))
