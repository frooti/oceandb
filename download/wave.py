from datetime import datetime, timedelta
from models import wave
from mongoengine import *

connect('ocean')

class wave(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	values = DictField()

## CONFIG ##
file_path = 'wave.dat'
date = datetime(day=1, month=9, year=2017) #GMT
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

		r = r.split()
		if len(r)==grid[1]: # process only if full row data is present
			for v in r:
				j += 1
				v = float(v)

				if v>=0.0:
					loc = {'type': 'Point', 'coordinates': [round(longitude1+(longitude_delta*(j-1)), 3), round(latitude1+(latitude_delta*(i-1)), 3)]}
					value = round(v, 3)
					year = date.year
					day = date.timetuple().tm_yday
					wave.objects(loc=loc).update_one(values__year__day=value, upsert=True)
					wave
		if i>grid[0]:
			i, j = (0, 0)
			date += timedelta 
