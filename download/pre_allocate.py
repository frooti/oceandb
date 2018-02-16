from download.models import tide, current
from datetime import datetime, timedelta
import copy
import scipy.io
from math import isnan

value = {}
base = {}

import pymongo
CONN = pymongo.MongoClient("mongodb://ocean:%40cean99@10.24.1.151/ocean?authSource=ocean")
DB = CONN['ocean']
CURRENT = DB.current
TIDE = DB.tide

# CONFIG #
file_path = '/tmp/tide/JANUARY/1_jan_tide.mat'
grid = (720, 1046)
date = datetime(hour=0, day=1, month=1, year=2018)
to_date = datetime(hour=0, day=1, month=1, year=2019)
# CONFIG #

MAT = scipy.io.loadmat(file_path)
LNG = MAT['data']['X'][0][0]
LAT = MAT['data']['Y'][0][0]
TIMESTEPS = 72

for t in range(0, TIMESTEPS):
	mins = str(int(date.hour*60)+int(date.minute))
	date += timedelta(days=0, hours=0, minutes=20)
	value[mins] = -99

date = datetime(hour=0, day=1, month=1, year=2018)

while date<to_date:         
	day = str(date.timetuple().tm_yday)
	date += timedelta(days=1)
	base[day] = copy.deepcopy(value)

for i in range(0, grid[0]-1):
	print i
	inserts = []
	for j in range(0, grid[1]-1):
		longitude = round(float(LNG[i][j]), 3)
		latitude = round(float(LAT[i][j]), 3)
		loc = {'type': 'Point', 'coordinates': [longitude, latitude]}
		if not isnan(longitude) and  not isnan(latitude):
			inserts.append({'l': loc, 'values': base})
	if inserts:
		CURRENT.insert_many(inserts)