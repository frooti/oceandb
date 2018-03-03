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
CURRENTDIRECTION = DB.currentdirection

## CONFIG ##
file_path = '/home/dataraft/projects/oceandb/currentdirection_timeseries.data'
## CONFIG ##

START = datetime.now()

def timeseries():
	with open(file_path) as f:
		bulk = CURRENTDIRECTION.initialize_unordered_bulk_op()

		for i, line in enumerate(f):
			print i
			line = line.strip().split('$')
			lng, lat = line[0].split(':')
			data = json.loads(line[1])
			
			# udpate_dict = {}
			# for day in data:
			# 	for mins in data[day]:
			# 		update_dict['values_'+day+'_'+mins] = data[day][mins]
			loc = {'type': 'Point', 'coordinates': [float(lng), float(lat)]}

			update_dict = {}
			for day in data:
				update_dict['values.'+day] = data[day]
			update_dict['l'] = loc

			bulk.find({'l':{'$geoIntersects': {'$geometry': loc}}}).upsert().update({'$set': update_dict})

			if i and i%1000==0:
				bulk.execute() # batch update
				bulk = CURRENTDIRECTION.initialize_unordered_bulk_op()
		
		bulk.execute() # left over
		print 'completed!'
		print 'TIME: '+str(datetime.now()-START)
		


if __name__ == '__main__':
	timeseries()
