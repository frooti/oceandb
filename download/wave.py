import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from datetime import datetime, timedelta
from mongoengine import *
from download.models import wave

connect('ocean', host='mongodb://13.229.95.21:27017/ocean')
#connect('ocean', host='13.229.95.21', port=27017)

## CONFIG ##
file_path = '/tmp/hs.txt'
now = datetime.now()
date = datetime(day=now.day, month=now.month, year=now.year) #GMT
timestep = timedelta(hours=24)
grid = (361, 321)
latitude1, longitude1 = (30.0, 30.0)
latitude2, longitude2 = (-50.0, 120.0)
## CONFIG ##

longitude_delta = (longitude2-longitude1)/(grid[0]-1)
latitude_delta = (latitude2-latitude1)/(grid[1]-1)

with open(file_path, 'r') as f:
	i, j = (0, 0)
	for r in f:
		i += 1
		print i
		r = r.split()
		if len(r)==grid[0]: # process only if full row data is present
			for v in r:
				j += 1
				#print j
				v = round(float(v), 2)

				if v>=0.0:
					loc = {'type': 'Point', 'coordinates': [round(longitude1+(longitude_delta*(j-1)), 3), round(latitude1+(latitude_delta*(i-1)), 3)]}
					value = round(v, 3)
					year = str(date.year)
					day = str(date.timetuple().tm_yday)
					data = {}
					data['set__values__'+year+'__'+day] = value
					data['upsert'] = True
					wave.objects(loc=loc).update_one(**data)
		if i==grid[1]:
			i = 0
			date += timestep
		if j==grid[0]:
			j = 0
