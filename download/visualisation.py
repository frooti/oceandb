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
	# The outer polyhedron.
	text = str(len(polygon))+' 2 0 1\n\n' # header
	for i, v in enumerate(polygon):
		text += str(i+1)+' '+str(v[0])+' '+str(v[1])+' 1'+'\n'
	# segments, each with a boundary marker.
	text += '\n'
	text += str(len(polygon))+' 1\n\n' # header
	for i in range(0, len(polygon)):
		if i==len(polygon)-1:
			text += str(i+1)+' '+str(i+1)+' '+str(1)+' 1'+'\n'
		else:
			text += str(i+1)+' '+str(i+1)+' '+str(i+2)+' 1'+'\n'
	# holes
	text += '\n'
	text += '0 \n\n' # header
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
	
	with open('/tmp/visualisation/'+z.zid+'.poly', 'w') as f:
		f.write(tri_data)

	out_bytes = subprocess.check_output(['triangle', '-pq25', '/tmp/visualisation/'+str(z.zid)+'.poly'])
	output = out_bytes.decode('utf-8')

	if 'Writing '+str(z.zid)+'.1.node' and 'Writing '+str(z.zid)+'.1.ele':
		vertices = tri_get_vertices('/tmp/visualisation/'+str(z.zid)+'.1.node')
		triangles = tri_get_triangles('/tmp/visualisation/'+str(z.zid)+'.1.ele')

		for t in triangles:
			t = transform_polygon([vertices[i-1] for i in t], origin=origin, reverse=True)
			rt = [[round(i[0], 6), round(i[1], 6)] for i in t]
			rt = rt+[rt[0]]
			centroid = [float(sum(col))/len(col) for col in zip(*rt)]

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

			# waveperiod
			waveperiod_value = None
			pipeline = [
					{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [rt]}}}} },
					{ "$group": {"_id": None, "height": { "$avg": "$values.1.0" }} },
				]
			q = list(waveperiod.objects.aggregate(*pipeline))
			if q:
				waveperiod_value = round(q[0].get('height', 0), 2)

			# wavedirection
			wavedirection_value = None
			wd = wavedirection.objects(loc__near=centroid).first()
			if wd:
				wavedirection_value = round(wd.values['1']['0'], 2) 

			# tide
			tide_value = None
			pipeline = [
					{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [rt]}}}} },
					{ "$group": {"_id": None, "height": { "$avg": "$values.121.12" }} },
				]
			q = list(tide.objects.aggregate(*pipeline))
			if q:
				tide_value = round(q[0].get('height', 0), 2)

			# current
			current_value = None
			c = current.objects(loc__near=centroid).first()
			if c:
				current_value = [round(c.values['121']['12'][0], 3), round(c.values['121']['12'][1], 0)]


			data.append([rt, waveheight_value, wavedirection_value, waveperiod_value, bathy_value, tide_value, current_value])
	
	z.triangles = data
	z.save()

