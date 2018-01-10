import sys
import os
from os import listdir
from os.path import isfile, join
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import uuid
from datetime import datetime, timedelta
from mongoengine import *
from download.models import zone, bathymetry

from scipy.spatial import ConvexHull
import csv

connect('ocean', host='mongodb://localhost:27017/ocean')

## CONFIG ##
directory = '/tmp/bathy_zones'
FILES = [os.path.join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]
## CONFIG ##

for file_path in FILES:
	print file_path
	
	with open(file_path, 'rb') as csvfile:
		# chull
		points = []
		chull  = []

		spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
		for i, row in enumerate(spamreader):
			if i==0:
				continue
			elif row:
				points.append([float(row[1]), float(row[0])])
		hull = ConvexHull(points)
		for i in hull.vertices:
			chull.append(points[i])

		chull = chull+[chull[0]]
		print chull
		# create zone
		z = zone(zid=str(uuid.uuid4()))
		z.ztype = 'bathymetry'
		z.name = file_path.split('/')[-1].split('.')[0]
		z.polygon = {'type': 'Polygon', 'coordinates': [chull]}
		z.save()

	with open(file_path, 'r') as f:
		data = []
		for i, r in enumerate(f):
			if i==0:
				continue
			elif i and i%3==0:
				bathymetry.objects.insert(data)
				data = []
				print i
			else:
				values = r.split('\t')
				if len(values)==3:
					longitute = float(values[1].strip())
					latitude = float(values[0].strip())
					depth = float(values[2].strip())*-1

				loc = {'type': 'Point', 'coordinates': [longitute, latitude]}
				data.append(bathymetry(loc=loc, depth=depth, zid=z.zid))
		else:
			if data:
				bathymetry.objects.insert(data)
			data = []
			print 'completed!'

