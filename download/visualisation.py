import os
import errno
import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import subprocess
from shapely.geometry import Polygon
import math
import numpy as np
from download.models import zone, wave, wavedirection, waveperiod, bathymetry, tide, current

try:
    os.makedirs('/tmp/visualisation')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise 

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
				triangles.append([int(v[1]), int(v[2]), int(v[3])])
	return triangles

def transform_polygon(polygon, origin, reverse=False):
	if reverse:
		return [[round(((v[0]/1.0e6)+origin[0]), 6), round(((v[1]/1.0e6)+origin[1]), 6)] for v in polygon]
	return [[round((v[0]-origin[0])*1.0e6, 0), round((v[1]-origin[1])*1.0e6, 0)] for v in polygon]

for z in zone.objects(ztype='zone'):
	print z.zid
	data = []
	origin = z.polygon['coordinates'][0][0]
	p = transform_polygon(z.polygon['coordinates'][0], origin=origin)
	tri_data = tri_input(p)
	
	with open('/tmp/visualisation/'+z.zid+'.node', 'w') as f:
		f.write(tri_data)

	out_bytes = subprocess.check_output(['triangle', '-25', '/tmp/visualisation/'+str(z.zid)+'.node'])
	output = out_bytes.decode('utf-8')

	if 'Writing '+str(z.zid)+'.1.node' and 'Writing '+str(z.zid)+'.1.ele':
		vertices = tri_get_vertices('/tmp/visualisation/'+str(z.zid)+'.1.node')
		triangles = tri_get_triangles('/tmp/visualisation/'+str(z.zid)+'.1.ele')

		for t in triangles:
			t = transform_polygon([vertices[i-1] for i in t], origin=origin, reverse=True)
			rt = [[round(i[0], 6), round(i[1], 6)] for i in t]
			rt = rt+[rt[0]]

			# bathymetry
			bathy_value = None
			pipeline = [
					{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [rt]}}}} },
					{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
				]
			q = list(bathymetry.objects.aggregate(*pipeline))
			if q:
				bathy_value = round(q[0].get('depth', 0), 2)

			# waveheight
			waveheight_value = None
			pipeline = [
					{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [rt]}}}} },
					{ "$group": {"_id": None, "height": { "$avg": "$values.1.0" }} },
				]
			q = list(wave.objects.aggregate(*pipeline))
			if q:
				waveheight_value = round(q[0].get('height', 0), 2)
			data.append([rt, waveheight_value, bathy_value])
	print data


