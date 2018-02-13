import sys 
sys.stdout.flush()

import math
import scipy.io
from math import isnan

from datetime import datetime, timedelta
import pymongo
CONN = pymongo.MongoClient("mongodb://ocean:%40cean99@10.24.1.151/ocean?authSource=ocean")
DB = CONN['ocean']
CURRENT = DB.current
CURRENTDIRECTION = DB.currentdirection

## CONFIG ##
file_path = '/Users/ravi/Desktop/current/uv/3.5_jan_current.mat'
grid = (720, 1046)
date = datetime(hour=12, day=1, month=1, year=2018) #GMT
timestep = timedelta(days=0, hours=0, minutes=20)
## CONFIG ##

MAT = scipy.io.loadmat(file_path)
LNG = MAT['data']['X'][0][0]
LAT = MAT['data']['Y'][0][0]
XVAL = MAT['data']['XComp'][0][0]
YVAL = MAT['data']['YComp'][0][0]
TIMESTEPS = len(XVAL)

for t in range(0, TIMESTEPS):
	print 'TIMESTEP: '+str(t)
	day = str(date.timetuple().tm_yday)
	mins = str(int(date.hour*60)+int(date.minute))
	date += timestep

	for i in range(0, grid[0]-1):
		print i
		bulk = CURRENT.initialize_unordered_bulk_op()
		bulk2 = CURRENTDIRECTION.initialize_unordered_bulk_op()
		
		for j in range(0, grid[1]-1):
			try:
				longitude = round(float(LNG[i][j]), 3)
				latitude = round(float(LAT[i][j]), 3)
				value = round(math.sqrt((XVAL[t][i][j]**2)+(YVAL[t][i][j]**2)), 3)
				direction = round(math.degrees(math.atan2(YVAL[t][i][j], XVAL[t][i][j])), 2)
				# if not isnan(direction) and direction<0:
				# 	direction += 360
				if not isnan(longitude) and  not isnan(latitude) and not isnan(value) and not isnan(direction):
					loc = {'type': 'Point', 'coordinates': [longitude, latitude]}
					bulk.find({'l':{'$geoIntersects': {'$geometry': loc}}}).upsert().update({'$set': {'l': loc, 'values.'+day+'.'+mins: value}})
					bulk2.find({'l':{'$geoIntersects': {'$geometry': loc}}}).upsert().update({'$set': {'l': loc, 'values.'+day+'.'+mins: direction}})
			except Exception, e:
				print e
		try:
			bulk.execute() # batch update
			bulk2.execute() # batch update
		except Exception, e:
			print e
print 'completed!'
