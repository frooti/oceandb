import os
import sys 
sys.stdout.flush()
import glob
import json
import gc

import scipy.io
from math import isnan

from datetime import datetime, timedelta

## CONFIG ##
file_path = '/var/www/dataraft.in/*_current_tide.mat'
output_path = 'current_timeseries.data'
grid = (720, 1046) # do not edit
date = datetime(day=1, month=1, year=2018) # GMT
timestep = timedelta(days=0, hours=0, minutes=20)
## CONFIG ##

DATA = {} # lat lng, timeseries

START = datetime.now()

#@profile
def timeseries():
	global date
	global START

	for f in sorted(glob.glob(file_path), key=lambda x: float('.'.join(x.split('/')[-1].split('_')[-1].split('.')[:-1]))):
		print 'PROCESSING: '+str(f)
		MAT = scipy.io.loadmat(f)
		LNG = MAT['data']['X'][0][0]
		LAT = MAT['data']['Y'][0][0]
		XVAL = MAT['data']['XComp'][0][0]
		YVAL = MAT['data']['YComp'][0][0]
		TIMESTEPS = len(XVAL)
		
		for t in range(0, TIMESTEPS):
			print 'TIMESTEP: '+str(t)
			day = str(date.timetuple().tm_yday)
			mins = '{}'.format(date.hour*60+date.minute)
			if t!=TIMESTEPS-1:
				date += timestep

			for i in range(0, grid[0]-1):
				for j in range(0, grid[1]-1):
					if not isnan(LNG[i][j]) and  not isnan(LAT[i][j]) and not isnan(XVAL[t][i][j]) and not isnan(YVAL[t][i][j]):t]):
						longitude = round(float(LNG[i][j]), 3)
						latitude = round(float(LAT[i][j]), 3)
						value = round(math.sqrt((XVAL[t][i][j]**2)+(YVAL[t][i][j]**2)), 3)
						#direction = round(math.degrees(math.atan2(YVAL[t][i][j], XVAL[t][i][j])), 2)
						#value = [speed, direction]
						
						key = '{}:{}'.format(longitude, latitude)
						if key not in DATA:
							DATA[key] = {}
						if day not in DATA[key]:
							DATA[key][day] = {}
						DATA[key][day][mins] = value
	
	print 'Writing to Output File ...'
	with open(output_path, 'a') as o:
		for l in DATA:
			o.write('{}${}{}'.format(l, json.dumps(DATA[l]), os.linesep))


	print 'completed!'
	print 'TIME: '+str(datetime.now()-START)

if __name__ == '__main__':
	timeseries()
