import os
import sys 
sys.stdout.flush()
import glob
import json
import gc
import numpy as np
import utm

import math
from math import isnan

from datetime import datetime, timedelta

## CONFIG ##
file_path = '/tmp/kk.dat'
output_path = 'oceancirculation_current_timeseries.data'
date = datetime(day=1, month=1, year=2018) # GMT
timestep = timedelta(days=0, hours=2, minutes=0)
UTM_ZONE = 45 
NODE_COUNT = 68604
ELEMENT_COUNT = 134659
## CONFIG ##

DATA = {}
NODE_KEY = {}

def timeseries():
	global date
	global DATA
	global NODE_KEY

	with open(file_path, 'r') as f:
		print 'PROCESSING: '+str(file_path)

		node = 0
		for line in f:
			line = line.strip().split(' ')
			if len(line)==9 or len(line)==4: # NODE
				if len(line)==9:
					try:
						line = [float(i) for i in line]
					except Exception, e:
						print e
						continue												
					node += 1
					lat, lng = utm.to_latlon(line[0], line[1], UTM_ZONE, 'U')
					u = line[3]
					v = line[4]
					speed = round(math.sqrt((u**2)+(v**2)), 3)
					direction = round(math.degrees(math.atan2(v, u)), 2)
					# NORTH
					if direction>0 and direction<=90: # Q1
						direction = 90-direction
					if direction>90 and direction<=180: # Q4
						direction = 450-direction
					if direction>-90 and direction<=0: # Q2
						direction = 90-direction
					if direction>-180 and direction<=-90: # Q3
						direction = 90-direction

					key = '{}:{}'.format(lng, lat)
					day = str(date.timetuple().tm_yday)
					mins = '{}'.format(date.hour*60+date.minute)
					NODE_KEY[node] = key
					DATA[key] = {}
					DATA[key][day] = {}
					DATA[key][day][mins] = [speed, direction]
				elif len(line)==4:
					line = [float(i) for i in line]
					node += 1
					u = line[1]
					v = line[2]
					speed = round(math.sqrt((u**2)+(v**2)), 3)
					direction = round(math.degrees(math.atan2(v, u)), 2)
					# NORTH
					if direction>0 and direction<=90: # Q1
						direction = 90-direction
					if direction>90 and direction<=180: # Q4
						direction = 450-direction
					if direction>-90 and direction<=0: # Q2
						direction = 90-direction
					if direction>-180 and direction<=-90: # Q3
						direction = 90-direction

					key = NODE_KEY[node]
					day = str(date.timetuple().tm_yday)
					mins = '{}'.format(date.hour*60+date.minute)
					if day in DATA[key]:
						DATA[key][day][mins] = [speed, direction]
					else:
						DATA[key][day] = {}
						DATA[key][day][mins] = [speed, direction]
			
			if node==NODE_COUNT:
				node = 0
				date += timestep
				print 'TIMESTEP: '+str(date)

	print 'Writing to Output File ...'
	with open(output_path, 'w') as o:
		for l in DATA:
			o.write('{}${}{}'.format(l, json.dumps(DATA[l]), os.linesep))


if __name__ == '__main__':
	START = datetime.now()
	timeseries()
	print 'TIME: '+str(datetime.now()-START)
	print 'completed!'