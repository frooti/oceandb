import sys 
sys.stdout.flush()

import scipy.io
from math import isnan

from datetime import datetime, timedelta
import pymongo
CONN = pymongo.MongoClient("mongodb://ocean:%40cean99@10.24.1.151/ocean?authSource=ocean")
DB = CONN['ocean']
TIDE = DB.tide_insert

## CONFIG ##
file_path = '/tmp/1_jan_tide.mat'
grid = (720, 1046) # do not edit
date = datetime(day=1, month=1, year=2018) # GMT
timestep = timedelta(days=0, hours=0, minutes=20)
## CONFIG ##

MAT = scipy.io.loadmat(file_path)
LNG = MAT['data']['X'][0][0]
LAT = MAT['data']['Y'][0][0]
VAL = MAT['data']['Val'][0][0]
TIMESTEPS = len(VAL)

START = datetime.now()

for t in range(0, TIMESTEPS):
	print 'TIMESTEP: '+str(t)
	day = str(date.timetuple().tm_yday)
	mins = str(int(date.hour*60)+int(date.minute))
	date += timestep

	for i in range(0, grid[0]-1):
		print i
		objects = []
		for j in range(0, grid[1]-1):
			try:
				longitude = round(float(LNG[i][j]), 3)
				latitude = round(float(LAT[i][j]), 3)
				value = round(float(VAL[t][i][j]), 3)
				if not isnan(longitude) and  not isnan(latitude) and not isnan(value):
					l = [longitude, latitude]
					v = [day, mins, value]
					objects.append({'l': l, 'v': v})
			except Exception, e:
				print e
		try:
			TIDE.insert_many(objects) # batch insert
		except Exception, e:
			print e

print 'completed!'
print 'TIME: '+str(datetime.now()-START)