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
for uz in userzone.objects():
	print uz.uzid
	data = []
	polygon = {'vertices': uz.polygon['coordinates'][0]}
	polygon['vertices'] = np.array(polygon['vertices'])
	
	tri = triangle.triangulate(polygon, opts='a.0125')
	 
	for t in tri['triangles']:
		t = [list(tri['vertices'][i]) for i in t]
		rt = [[round(i[0], 5), round(i[1], 5)] for i in t]
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

	uz.triangles = data
	uz.save()

# public zones
for z in zone.objects(ztype='bathymetry'):
	print z.zid
	data = []
	mesh_info = MeshInfo()
	interpolated_chull = z.polygon['coordinates'][0][:] #interpolate_polygon(z.polygon)
	# to_int
	interpolated_chull = [[int(v[0]*1e8), int(v[1]*1e8)] for v in interpolated_chull]

	mesh_info = MeshInfo()
	mesh_info.set_points(interpolated_chull)
	facets = [(i, i+1) for i in range(0, len(interpolated_chull)-1)]
	mesh_info.set_facets(facets)
	mesh = build(mesh_info)
	
	for t in mesh.elements:
		t = [[mesh.points[i][0]/1.0e8, mesh.points[i][1]/1.0e8]  for i in t]
		rt = [[round(i[0], 5), round(i[1], 5)] for i in t]
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

	
	z.triangles = data
	z.save()