import sys 
sys.stdout.flush()

import math
import scipy.io
from math import isnan

from datetime import datetime, timedelta
import pymongo
CONN = pymongo.MongoClient("mongodb://ocean:%40cean99@10.24.1.151/ocean?authSource=ocean")
DB = CONN['ocean']
TIDE = DB.tide

## CONFIG ##
file_path = '/tmp/current.mat'
grid = (720, 1046)
date = datetime(day=1, month=5, year=2017) #GMT
timestep = timedelta(hours=12)
## CONFIG ##

MAT = scipy.io.loadmat(file_path)
LNG = MAT['data']['X'][0][0]
LAT = MAT['data']['Y'][0][0]
XVAL = MAT['data']['XComp'][0][0]
YVAL = MAT['data']['YComp'][0][0]
TIMESTEPS = len(VAL)

for t in range(0, TIMESTEPS):
	print 'TIMESTEP: '+str(t)
	day = str(date.timetuple().tm_yday)
	hour = str(int(date.hour))
	date += timestep

	for i in range(0, grid[0]-1):
		print i
		bulk = TIDE.initialize_unordered_bulk_op()
		
		for j in range(0, grid[1]-1):
			try:
				longitude = round(float(LNG[i][j]), 3)
				latitude = round(float(LAT[i][j]), 3)
				value = math.sqrt((XVAL[t][i][j]**2)+(YVAL[t][i][j]**2))
				direction = math.degrees(math.arctan2(YVAL[t][i][j], XVAL[t][i][j]))
				if direction<0:
					direction += 360
				if not isnan(longitude) and  not isnan(latitude) and not isnan(value):
					loc = {'type': 'Point', 'coordinates': [longitude, latitude]}
					bulk.find({'l':{'$geoIntersects': {'$geometry': loc}}}).upsert().update({'$set': {'l': loc, 'values.'+day+'.'+hour: [value, direction]}})
			except Exception, e:
				print e
		try:
			bulk.execute() # batch update
		except Exception, e:
			print e
print 'completed!'
