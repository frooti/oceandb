import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from meshpy.triangle import MeshInfo, build
import triangle
import math
import numpy as np
from download.models import zone, userzone, bathymetry, userbathymetry

dmax = 10.0e-04
def interpolate_polygon(polygon): # geojson
	vertices = []
	for i in range(0, len(polygon['coordinates'][0])-1): # for each edge
		v1 = [round(polygon['coordinates'][0][i][0], 6), round(polygon['coordinates'][0][i][1], 6)]
		v2 = [round(polygon['coordinates'][0][i+1][0], 6), round(polygon['coordinates'][0][i+1][1], 6)]
		di = math.hypot(v2[1]-v1[1], v2[0]-v1[0])
		ui = [(v2[0]-v1[0])/di, (v2[1]-v1[1])/di]
		

		if di>dmax: # interpolate
			vertices.append(v1)
			for j in range(0, int(di/dmax)):
				vi = [round(v1[0]+(((j+1)*dmax)*ui[0]), 6), round(v1[1]+(((j+1)*dmax)*ui[1]), 6)]
				vertices.append(vi)
		else:
			vertices.append(v1)
		
	return vertices+[vertices[0]]

# user zones
# for uz in userzone.objects():
# 	print uz.uzid
# 	data = []
# 	interpolated_chull = interpolate_polygon(uz.polygon)
# 	interpolated_chull = [[int(v[0]*1e8), int(v[1]*1e8)] for v in interpolated_chull]
# 	polygon = {'vertices': interpolated_chull}
# 	polygon['vertices'] = np.array(polygon['vertices'])
	
# 	tri = triangle.triangulate(polygon, opts='q')
	 
# 	for t in tri['triangles']:
# 		t = [list(tri['vertices'][i]) for i in t]
# 		t = [[i[0]/1.0e8, i[1]/1.0e8] for i in t]
# 		rt = [[round(i[0], 8), round(i[1], 8)] for i in t]
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
# 			#print e
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

# 	uz.triangles = data
# 	uz.save()

# public zones
for z in zone.objects(ztype='bathymetry'):
	print z.zid
	data = []
	mesh_info = MeshInfo()
	mesh_info.set_points(z.polygon['coordinates'][0])
	facets = [(i, i+1) for i in range(0, len(z.polygon['coordinates'][0])-1)]
	mesh_info.set_facets(facets)
	mesh = build(mesh_info)

	for t in mesh.elements:
		t = [list(tri['vertices'][i]) for i in t]
		rt = [[round(i[0], 8), round(i[1], 8)] for i in t]
		rt = rt+[rt[0]]
		try:
			pipeline = [
				{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [rt]}}}} },
				{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
			]
			value = 0
			q = list(bathymetry.objects.aggregate(*pipeline))
			if q:
				value = round(q[0].get('depth', 0), 2)
			data.append([rt, value])
		except Exception, e:
			#print e
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

	
	z.triangles = data
	z.save()