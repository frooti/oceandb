import os
import sys 
sys.stdout.flush()
import glob
import json
import gc

import scipy.io
from math import isnan

from datetime import datetime, timedelta
import pymongo
CONN = pymongo.MongoClient("mongodb://ocean:%40cean99@10.24.1.151/ocean?authSource=ocean")
DB = CONN['ocean']
TIDE = DB.tide

## CONFIG ##
file_path = '/home/dataraft/projects/oceandb/tide_timeseries.data'
## CONFIG ##

START = datetime.now()

def timeseries():
	with open(file_path) as f:
		bulk = TIDE.initialize_unordered_bulk_op()

		for i, line in enumerate(f):
			print i
			line = line.strip().split('$')
			lng, lat = line[0].split(':')
			data = json.loads(line[1])
			
			update_dict = {}
			for day in data:
				for mins in data[day]:
					update_dict['values.'+day+'.'+mins] = data[day][mins]

			loc = {'type': 'Point', 'coordinates': [lng, lat]}
			update_dict['l'] = loc
			bulk.find({'l':{'$geoIntersects': {'$geometry': loc}}}).upsert().update({'$set': update_dict})

			if i and i%1000==0:
				bulk.execute() # batch update
				bulk = TIDE.initialize_unordered_bulk_op()
		
		bulk.execute() # left over
		print 'completed!'
		print 'TIME: '+str(datetime.now()-START)
		


if __name__ == '__main__':
	timeseries()
