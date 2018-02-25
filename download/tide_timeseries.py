import sys 
sys.stdout.flush()
import glob
import json

import scipy.io
from math import isnan

from datetime import datetime, timedelta

## CONFIG ##
file_path = '/Users/ravi/Downloads/*_jan_tide.mat'
grid = (720, 1046) # do not edit
date = datetime(day=1, month=1, year=2018) # GMT
timestep = timedelta(days=0, hours=0, minutes=20)
## CONFIG ##

DATA = {} # lat lng, timeseries

START = datetime.now()

for f in glob.glob(file_path):
	print 'PROCESSING: '+str(f)
	MAT = scipy.io.loadmat(f)
	LNG = MAT['data']['X'][0][0]
	LAT = MAT['data']['Y'][0][0]
	VAL = MAT['data']['Val'][0][0]
	TIMESTEPS = len(VAL)

	for t in range(0, TIMESTEPS):
		print 'TIMESTEP: '+str(t)
		day = str(date.timetuple().tm_yday)
		mins = str(int(date.hour*60)+int(date.minute))
		date += timestep

		for i in range(0, grid[0]-1):
			for j in range(0, grid[1]-1):
				longitude = round(float(LNG[i][j]), 3)
				latitude = round(float(LAT[i][j]), 3)
				value = round(float(VAL[t][i][j]), 3)
				if not isnan(longitude) and  not isnan(latitude) and not isnan(value):
					key = str(longitude)+':'+str(latitude)
					if key not in DATA:
						DATA[key] = {}
					if day not in DATA[key]:
						DATA[key][day] = {}
					DATA[key][day][mins] = value


print 'Writing to Output File ...'
o = open('tide_timeseries.json', 'w')
o.write(json.dumps(DATA))

print 'completed!'
print 'TIME: '+str(datetime.now()-START)