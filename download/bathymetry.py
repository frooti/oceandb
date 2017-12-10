import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from datetime import datetime, timedelta
from download.models import bathymetry 
from mongoengine import *

connect('ocean', host='mongodb://localhost:27017/ocean')

## CONFIG ##
file_path = '/tmp/bathy_data'
## CONFIG ##

with open(file_path, 'r') as f:
	data = []
	for i, r in enumerate(f):
		if i and i%1000==0:
			bathymetry.objects.insert(data)
			data = []
			print i
		else:
			values = r.split(',')
			longitute = float(values[0])
			latitude = float(values[1])
			depth = float(values[2])

			loc = {'type': 'Point', 'coordinates': [longitute, latitude]}
			data.append(bathymetry(loc=loc, depth=depth))
	else:
		if data:
			bathymetry.objects.insert(data)
		data = []
		print 'completed!'
