import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from download.alpha_shape import alpha_shape
import triangle # mesh generator
from shapely.ops import triangulate # Delauny
from shapely.geometry import Point, MultiPoint, Polygon, MultiPolygon
from shapely.geometry import shape
from shapely.geometry import mapping
from shapely.ops import cascaded_union
import numpy as np
from download.models import zone, userzone, bathymetry, userbathymetry

# user zones
for uz in userzone.objects():
	data = []
	points = [shape(p.loc) for p in userbathymetry.objects(uzid=uz.uzid)]
	# alpha shape
	concave_polygon = alpha_shape(points, 0.4)
	uz.concave_polygon = concave_polygon
	uz.save()
	polygon = {'vertices': concave_polygon['coordinates'][0]}
 	polygon['vertices'] = np.array(polygon['vertices'])
	# meshing
	tri = triangle.triangulate(polygon, opts='q50')

	for t in tri['triangles']:
		t = [list(tri['vertices'][i]) for i in t]
 		rt = [[round(i[0], 5), round(i[1], 5)] for i in t]
 		rt = rt+[rt[0]]
		
		try:
			pipeline = [
				{ "$match": {'l': {'$geoIntersects': {'$geometry':t}}} },
				{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
			]
			value = 0
			q = list(userbathymetry.objects.aggregate(*pipeline))
			if q:
				value = round(q[0].get('depth', 0), 1)
			data.append([rt, value])
		except Exception, e:
 			print e
 			t = t+[t[0]]
 			pipeline = [
 				{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [t]}}}} },
 				{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
 			]
 			value = 0
 			q = list(bathymetry.objects.aggregate(*pipeline))
 			if q:
 				value = round(q[0].get('depth', 0), 2)
 			data.append([t, value])

 	print len(data)
	#uz.triangles = data
	#uz.save()

# public zones
# for z in zone.objects(ztype='bathymetry'):
# 	data = []
# 	polygon = {'vertices': z.polygon['coordinates'][0]}
# 	polygon['vertices'] = np.array(polygon['vertices'])
	
# 	tri = triangle.triangulate(polygon, opts='q25D')
	 
# 	for t in tri['triangles']:
# 		t = [list(tri['vertices'][i]) for i in t]
# 		rt = [[round(i[0], 5), round(i[1], 5)] for i in t]
# 		rt = rt+[rt[0]]
# 		try:
# 			pipeline = [
# 				{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [rt]}}}} },
# 				{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
# 			]
# 			value = 0
# 			q = list(bathymetry.objects.aggregate(*pipeline))
# 			if q:
# 				value = round(q[0].get('depth', 0), 2)
# 			data.append([rt, value])
# 		except Exception, e:
# 			print e
# 			t = t+[t[0]]
# 			pipeline = [
# 				{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [t]}}}} },
# 				{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
# 			]
# 			value = 0
# 			q = list(bathymetry.objects.aggregate(*pipeline))
# 			if q:
# 				value = round(q[0].get('depth', 0), 2)
# 			data.append([t, value])

	
# 	z.triangles = data
# 	z.save()