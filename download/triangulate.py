import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import triangle
import numpy as np
from download.models import zone, userzone, bathymetry, userbathymetry

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
	polygon = {'vertices': z.polygon['coordinates'][0]}
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

	
	z.triangles = data
	z.save()