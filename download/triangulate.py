import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import triangle
import numpy as np
from download.models import zone, userzone, bathymetry, userbathymetry

# user zones
for uz in userzone.objects():
	data = []
	polygon = {'vertices': uz.polygon['coordinates'][0]}
	polygon['vertices'] = np.array(polygon['vertices'])
	
	tri = triangle.triangulate(polygon, opts='qa0.01')
	 
	for t in tri['triangles']:
		t = [list(tri['vertices'][i]) for i in t]
		t = t+[t[0]]
		pipeline = [
			{ "$match": {'l': {'$geoIntersects': {'$geometry': {'type': 'Polygon', 'coordinates': [t]}}}} },
			{ "$group": {"_id": None, "depth": { "$avg": "$d" }} },
		]
		value = 0
		q = list(bathymetry.objects.aggregate(*pipeline))
		if q:
			value = round(q[0].get('depth', 0), 2)

	uz.triangles = data
	uz.save()

# public zones
for z in zone.objects(ztype='bathymetry'):
	data = []
	polygon = {'vertices': z.polygon['coordinates'][0]}
	polygon['vertices'] = np.array(polygon['vertices'])
	
	tri = triangle.triangulate(polygon, opts='qa0.01')
	 
	for t in tri['triangles']:
		t = [list(tri['vertices'][i]) for i in t]
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