import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import json
from download.models import zone, zonedata, wave, wavedirection, waveperiod, bathymetry, tide, current, currentdirection

for z in zone.objects(zid='b951a954-f3f7-44f6-80a6-0194cbee50a1'):
	print z.zid, z.name

	feature_coll = {
		"type" : "FeatureCollection",
		"features" : []
	}

	# fetch data
	current_data = {}
	print 'fetch current...'
	for c in current.objects(loc__geo_intersects=z.polygon):
		key = ','.join([str(i) for i in c.loc['coordinates']])
		value = c.values['1']['0']
		if key in current_data:
			current_data[key]['s'] = value
		else:
			 current_data[key] = {'s': value}

	print 'fetch direction...'
	for cd in currentdirection.objects(loc__geo_intersects=z.polygon):
		key = ','.join([str(i) for i in cd.loc['coordinates']])
		value = cd.values['1']['0']
		if key in current_data:
			current_data[key]['d'] = value
		else:
			current_data[key] = {'d': value}

	for d in current_data:
		lng, lat = [float(i) for i in d.split(',')]
		speed = current_data[d]['s']
		direction = current_data[d]['d']

		feature = {
			"type" : "Feature",
			"properties" : {
				"s": speed,
				"d": direction
			},
			"geometry" : {
				"type" : "Point",
				"coordinates" : [lng, lat]
			}
		}

		feature_coll['features'].append(feature)

	with open('feature_collection.json', 'w') as f:
		f.write(json.dumps(feature_coll))
