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
## CONFIG ##

mat = scipy.io.loadmat(file_path)
lng = mat['data']['X'][0][0]
lat = mat['data']['Y'][0][0]
val = mat['data']['Val'][0][0]

i, j = 0, 0

for i in range(0, grid[0]):
	print i
	bulk = TIDE.initialize_unordered_bulk_op()
	
	for j in range(0, grid[1]):
		try:
			longitude = round(float(lng[i][j]), 3)
			latitude = round(float(lat[i][j]), 3)
			value = float('1.0')
			if not isnan(longitude) and  not isnan(latitude) and not isnan(value):
				loc = {'type': 'Point', 'coordinates': [longitude, latitude]}
				bulk.find({'l':{'$geoIntersects': {'$geometry': loc}}}).upsert().update({'$set': {'l': loc, 'h': value}})
		except Exception, e:
			print e
	try:
		bulk.execute() # batch update
	except Exception, e:
		print e
