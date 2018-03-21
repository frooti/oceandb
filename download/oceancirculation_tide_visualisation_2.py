import os
import sys 
sys.stdout.flush()
import glob
import json
import gc

from datetime import datetime, timedelta
import dateutil.parser
import pymongo
CONN = pymongo.MongoClient("mongodb://ocean:%40cean99@10.24.1.151/ocean?authSource=ocean")
DB = CONN['ocean']
TIDE_VIS = DB.tide_visualisation

## CONFIG ##
zid = 'test-project'
file_path = 'oceancirculation_tide_visualisation.data'
## CONFIG ##

START = datetime.now()

def upload():
	with open(file_path) as f:
		objects = []
		for i, line in enumerate(f):
			print i
			line = line.strip().split('$$')
			polygon = json.loads(line[0])
			depth = float(line[1])
			date = dateutil.parser.parse(line[2])

			objects.append({'zid':zid, 'p':polygon, 'd':depth, 'dt':date})
			
			if i%1000==0:
				TIDE_VIS.insert_many(objects) # batch insert
				objects = []

		TIDE_VIS.insert_many(objects) # left over
		print 'completed!'
		print 'TIME: '+str(datetime.now()-START)

if __name__ == '__main__':
	upload()