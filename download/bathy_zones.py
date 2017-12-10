import sys
import os
from os import listdir
from os.path import isfile, join
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from datetime import datetime, timedelta
from mongoengine import *
from download.models import bathymetry

connect('ocean', host='mongodb://localhost:27017/ocean')

## CONFIG ##
directory = '/tmp/bathy_zones'
FILES = [os.path.join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]
## CONFIG ##

for file_path in FILES:
	print file_path

	with open(file_path, 'r') as f:
		data = []
		for i, r in enumerate(f):
			if i==0:
				continue
			elif i and i%1==0:
				bathymetry.objects.insert(data)
				data = []
				print i
			else:
				values = r.split('\t')
				if len(values)==3:
					longitute = float(values[1].strip())
					latitude = float(values[0].strip())
					depth = float(values[2].strip())

				loc = {'type': 'Point', 'coordinates': [longitute, latitude]}
				data.append(bathymetry(loc=loc, depth=depth))
		else:
			bathymetry.objects.insert(data)
			data = []
			print 'completed!'

