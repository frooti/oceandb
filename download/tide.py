import sys 
sys.stdout.flush()

import scipy.io
from math import isnan

from datetime import datetime, timedelta
import pymongo
CONN = pymongo.MongoClient("mongodb://ocean:%40cean99@10.24.1.151/ocean?authSource=ocean")
DB = CONN['ocean']
TIDE = DB.tide

## CONFIG ##
file_path = '/tmp/tide.mat'
grid = (720, 1046)
date = datetime(day=1, month=5, year=2017) #GMT
timestep = timedelta(hours=12)
## CONFIG ##

MAT = scipy.io.loadmat(file_path)
LNG = MAT['data']['X'][0][0]
LAT = MAT['data']['Y'][0][0]
VAL = MAT['data']['Val'][0][0]
TIMESTEPS = len(VAL)

for t in range(0, TIMESTEPS):
	print 'TIMESTEP: '+str(t)
	day = str(date.timetuple().tm_yday)
	hour = str(int(date.hour))
	date += timestep

	for i in range(0, grid[0]):
		print i
		bulk = TIDE.initialize_unordered_bulk_op()
		
		for j in range(0, grid[1]):
			try:
				longitude = round(float(lng[i][j]), 3)
				latitude = round(float(lat[i][j]), 3)
				value = float(VAL[t][i][j])
				if not isnan(longitude) and  not isnan(latitude) and not isnan(value):
					loc = {'type': 'Point', 'coordinates': [longitude, latitude]}
					bulk.find({'l':{'$geoIntersects': {'$geometry': loc}}}).upsert().update({'$set': {'l': loc, 'values.'+day+'.'+hour: value}})
			except Exception, e:
				print e
		try:
			bulk.execute() # batch update
		except Exception, e:
			print e
