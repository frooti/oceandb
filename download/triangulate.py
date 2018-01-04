import os
import errno
import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import subprocess
from shapely.geometry import Polygon
import math
import numpy as np
from download.models import zone, userzone, bathymetry, userbathymetry

try:
    os.makedirs('/tmp/triangle')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

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

def tri_input(polygon):
	text = str(len(polygon))+' 2 0 0\n\n' # header
	for i, v in enumerate(polygon):
		text += str(i+1)+' '+str(v[0])+' '+str(v[1])+'\n'
	return text

def tri_get_vertices(file):
	vertices = []
	f = open(file, 'r')
	for i, l in enumerate(f):
		if i==0:
			continue
		else:
			v = l.split()
			if v[0]!='#':
				vertices.append([float(v[1]), float(v[2])])
	return vertices

def tri_get_triangles(file):
	triangles = []
	f = open(file, 'r')
	for i, l in enumerate(f):
		if i==0:
			continue
		else:
			v = l.split()
			if v[0]!='#':
				triangles.append([float(v[1]), float(v[2]), float(v[3])])
	return triangles

def transform_polygon(polygon, origin, reverse=False):
	if reverse:
		return [[round(((v[0]/1.0e6)+origin[0]), 6), round(((v[1]/1.0e6)+origin[1]), 6)] for v in polygon]
	return [[round((v[0]-origin[0])*1.0e6, 0), round((v[1]-origin[1])*1.0e6, 0)] for v in polygon]

# user zones
# for uz in userzone.objects():
# 	print uz.uzid
# 	data = []
# 	mesh_info = MeshInfo()
# 	origin = uz.polygon['coordinates'][0][0]
# 	p = transform_polygon(uz.polygon['coordinates'][0], origin=origin)
# 	mesh_info.set_points(p)
# 	facets = [(i, i+1) for i in range(0, len(p)-1)]
# 	mesh_info.set_facets(facets)
# 	max_volume = int(Polygon(p).area/200)
# 	mesh = build(mesh_info, max_volume=max_volume)
	
# 	for t in mesh.elements:
# 		t = transform_polygon([mesh.points[i] for i in t], origin=origin, reverse=True)
# 		rt = [[round(i[0], 6), round(i[1], 6)] for i in t]
# 		rt = rt+[rt[0]]
# 		try:
# 			pipeline = [
# 				{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [rt]}}}} },
# 				{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
# 			]
# 			value = 0
# 			q = list(userbathymetry.objects.aggregate(*pipeline))
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
# 			q = list(userbathymetry.objects.aggregate(*pipeline))
# 			if q:
# 				value = round(q[0].get('depth', 0), 2)
# 			data.append([t, value])

# 	uz.triangles = data
# 	uz.save()

# public zones
for z in zone.objects(ztype='bathymetry'):
	print z.zid
	data = []
	origin = z.polygon['coordinates'][0][0]
	p = transform_polygon(z.polygon['coordinates'][0], origin=origin)
	tri_data = tri_input(p)
	
	with open('/tmp/triangle/'+z.zid+'.node', 'w') as f:
		f.write(tri_data)
		
	max_area = int(Polygon(p).area/200)
	out_bytes = subprocess.check_output(['triangle', '-a'+str(max_area), '/tmp/triangle/'+str(z.zid)+'.node'])
	output = out_bytes.decode('utf-8')

	if 'Writing '+str(z.zid)+'.1.node' and 'Writing '+str(z.zid)+'.1.ele':
		vertices = tri_get_vertices('/tmp/triangle/'+str(z.zid)+'.1.node')
		triangles = tri_get_triangles('/tmp/triangle/'+str(z.zid)+'.1.ele')

		print 'vertices: '+str(vertices)
		print 'triangles: '+str(triangles)

	# for t in mesh.elements:
	# 	t = transform_polygon([mesh.points[i] for i in t], origin=origin, reverse=True)
	# 	rt = [[round(i[0], 6), round(i[1], 6)] for i in t]
	# 	rt = rt+[rt[0]]
	# 	try:
	# 		pipeline = [
	# 			{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [rt]}}}} },
	# 			{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
	# 		]
	# 		value = 0
	# 		q = list(bathymetry.objects.aggregate(*pipeline))
	# 		if q:
	# 			value = round(q[0].get('depth', 0), 2)
	# 		data.append([rt, value])
	# 	except Exception, e:
	# 		#print e
	# 		t = t+[t[0]]
	# 		pipeline = [
	# 			{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [t]}}}} },
	# 			{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
	# 		]
	# 		value = 0
	# 		q = list(bathymetry.objects.aggregate(*pipeline))
	# 		if q:
	# 			value = round(q[0].get('depth', 0), 2)
	# 		data.append([t, value])

	
	# z.triangles = data
	# z.save()