import os
import errno
import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from datetime import datetime
import calendar
import subprocess
from shapely.geometry import Polygon
import math
import numpy as np
from download.models import zone, wave, wavedirection, waveperiod, bathymetry, tide, current, currentdirection

try:
    os.makedirs('/tmp/visualisation')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise 

### CACHE ###
import redis
import json
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
REDIS = redis.Redis(connection_pool=pool)
### CACHE ###

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

def monthToDate(month):
	from_date = datetime(day=1, month=int(month), year=2018)
	to_date = datetime(day=calendar.monthrange(2018, int(month))[1], month=int(month), year=2018)
	return from_date, to_date

def monthly_values(values, type=None):
	data = {}
	year = 2018
	for m in range(1, 13):
		from_date, to_date = monthToDate(m)
		from_day, to_day = from_date.timetuple().tm_yday, to_date.timetuple().tm_yday
		
		if type=='high':
			highest = None
			while from_day<=to_day:
				try:
					for k in values[str(from_day)]:
						v = values[str(from_day)][k]
						if v and v>highest:
							highest = v
				except:
					pass
				from_day += 1
			data[str(m)] = highest
		else:
			try:
				v = values[str(from_day)]['0']
				data[str(m)] = v
			except:
				pass
	return data




for z in zone.objects(ztype='zone'):
	print z.zid, z.name
	data = []
	origin = z.polygon['coordinates'][0][0]
	p = transform_polygon(z.polygon['coordinates'][0], origin=origin)
	tri_data = tri_input(p)
	
	with open('/tmp/visualisation/'+z.zid+'.poly', 'w') as f:
		f.write(tri_data)

	max_area = int(Polygon(p).area/400)
	out_bytes = subprocess.check_output(['triangle', '-pq25a'+str(max_area), '/tmp/visualisation/'+str(z.zid)+'.poly'])
	output = out_bytes.decode('utf-8')

	if 'Writing '+str(z.zid)+'.1.node' and 'Writing '+str(z.zid)+'.1.ele':
		vertices = tri_get_vertices('/tmp/visualisation/'+str(z.zid)+'.1.node')
		triangles = tri_get_triangles('/tmp/visualisation/'+str(z.zid)+'.1.ele')
		print 'TRIANGLES: '+str(len(triangles))

		for i, t in enumerate(triangles):
			print i
			t = transform_polygon([vertices[i-1] for i in t], origin=origin, reverse=True)
			rt = [[round(i[0], 6), round(i[1], 6)] for i in t]
			centroid = [float(sum(col))/len(col) for col in zip(*rt)]
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
			waveheight_value = {}
			w = wave.objects(loc__near=centroid).first()
			if w:
				values = w.values
				waveheight_value = monthly_values(values)
			
			# waveperiod
			waveperiod_value = {}
			wp = waveperiod.objects(loc__near=centroid).first()
			if wp:
				values = wp.values
				waveperiod_value = monthly_values(values)
			
			# wavedirection
			wavedirection_value = {}
			wd = wavedirection.objects(loc__near=centroid).first()
			if wd:
				values = wd.values
				wavedirection_value = monthly_values(values)

			# tide
			tide_value = {}
			t = tide.objects(loc__near=centroid).first()
			if t:
				values = t.values
				tide_value = monthly_values(values)

			# current
			current_value = {}
			c = current.objects(loc__near=centroid).first()
			if c:
				values = t.values
				current_value = monthly_values(values)

			# currentdirection
			currentdirection_value = {}
			cd = currentdirection.objects(loc__near=centroid).first()
			if cd:
				values = cd.values
				currentdirection_value = monthly_values(values)


			data.append([rt, waveheight_value, wavedirection_value, waveperiod_value, bathy_value, tide_value, current_value, currentdirection_value])
	
	z.triangles = data
	z.save()

	REDIS.set(z.zid, '{}${}'.format(z.ztype, json.dumps(z.triangles)))

