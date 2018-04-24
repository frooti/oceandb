import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import scipy.io
from shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, current, currentdirection, current_visualisation
from datetime import datetime, timedelta

## CONFIG ##
zid = ''
## CONFIG ##

def visualisation():
	elements = []
	for c in current.objects(zid=zid):
		try:
			point = asShape(c.loc)
			if point.is_valid:
				elements.append(point)
		except:
			pass

	for z in zone.objects(ztype='project', zid=zid):
		print 'PROCESSING: '+str(z.zid)+' '+str(z.name)
		zpolygon = asShape(z.polygon)
		for e in elements:
			if zpolygon.intersects(e):
				print mapping(e)
				point = current.objects(zid=zid, loc__geo_intersects=mapping(e)).first()
				point2 = currentdirection.objects(zid=zid, loc__geo_intersects=mapping(e)).first()

				if point and point2:
					point = point['values']
					point2 = point2['values']
					data = []
					for i in range(1,366):
						if data:
							current_visualisation.objects.insert(data)
							data = []
						if str(i) in point and str(i) in point2:
							cv = current_visualisation(zid=z.zid)
							cv.date = datetime(year=2018, month=1, day=1)+timedelta(days=i-1)
							cv.loc = mapping(e)
							cv.speed = point[str(i)]['0']
							cv.direction = point2[str(i)]['0']
							data.append(cv)
					else:
						if data:
							current_visualisation.objects.insert(data)
							data = []

if __name__ == '__main__':
	START = datetime.now()
	visualisation()
	print 'TIME: '+str(datetime.now()-START)
	print 'completed!'