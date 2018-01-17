import sys 
sys.stdout.flush()

import scipy.io


from datetime import datetime, timedelta
import pymongo
CONN = pymongo.MongoClient('10.24.1.151', 27017, username='ocean', password='@cean99', authMechanism='MONGODB-CR')
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

while i<grid[0]:
	print i
	bulk = TIDE.initialize_unordered_bulk_op()
	
	while j<grid[1]:
		try:
			loc = {'type': 'Point', 'coordinates': [round(float(lng[i][j]), 3), round(float(lat[i][j]), 3)}
			height = float('1.0')
			bulk.find({'l':{'$geoIntersects': {'$geometry': loc}}}).upsert().update({'$set': {'l': loc, 'height': height}})
			j = j+1
		except:
			pass
	bulk.execute() # batch update
	i = i+1
	j = 0
