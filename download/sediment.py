import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from datetime import datetime, timedelta
from download.models import zone, sediment
from mongoengine import *
from shapely.geometry import asShape, mapping

db = connect('ocean', host='mongodb://localhost:27017/ocean', username='ocean', password='@cean99')
db["ocean"].authenticate("ocean", password="@cean99")

## CONFIG ##
file_path = '/tmp/sediment.csv'
## CONFIG ##

with open(file_path, 'r') as f:
	data = []
	for i, r in enumerate(f):
		if i<2:
			continue

		if i and i%10==0:
				sediment.objects.insert(data)
				data = []
				print i
		else:
			values = r.split(',')
			longitute = float(values[1])
			latitude = float(values[2])
			angle = float(values[3])
			# Tranform to EAST
			if angle>0 and angle<=90: #Q1
				angle = 90-angle
			if angle>90 and angle<=180: #Q2
				angle = 470-angle
			if angle>180 and angle<=270: #Q3
				angle = 450-angle
			if angle>270 and angle<=360: #Q4
				angle = 450-angle
			
			zid = None
			for z in zone.objects(ztype='zone'):
				zpolygon = asShape(z.polygon)
				point = asShape({'type':'Point', 'coordinates':[longitute, latitude]})
				if zpolygon.intersects(point):
					zid = z.zid
			if zid:
				for i in range(1, 13):
					month = i
					quantity = float(values[i+3])
					if quantity:
						loc = {'type': 'Point', 'coordinates': [longitute, latitude]}
						data.append(sediment(loc=loc, value=quantity, month=month, angle=angle))
	else:
		if data:
			sediment.objects.insert(data)
		data = []
		print 'completed!'
