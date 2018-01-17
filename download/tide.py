import sys 
sys.stdout.flush()

import scipy.io


from datetime import datetime, timedelta
import pymongo
CONN = pymongo.MongoClient('localhost', 27017, username='ocean', password='@cean99', authMechanism='MONGODB-CR')
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
	while j<grid[1]:
		print lng[i][j], lat[i][j]
		j = j+1
	i = i+1