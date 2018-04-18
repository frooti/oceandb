import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import scipy.io
from shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, wave, wavedirection, wavedirection_visualisation
from datetime import datetime, timedelta

## CONFIG ##
GRID = (321, 361)
latitude1, longitude1 = (30.0, 30.0)
latitude2, longitude2 = (-50.0, 120.0)
## CONFIG ##

longitude_delta = (longitude2-longitude1)/(GRID[1]-1)
latitude_delta = (latitude2-latitude1)/(GRID[0]-1)

def visualisation():
	elements = []
	for i in range(0, GRID[0]):
		for j in range(0, GRID[1]):
			p = [round(longitude1+(longitude_delta*j), 3), round(latitude1+(latitude_delta*i), 3)]
			try:
				point = asShape({'type': 'Point', 'coordinates': p})
				if point.is_valid:
					elements.append(point)
			except:
				pass

	for z in zone.objects(zid='b3913413-5b23-4021-a41b-182166e9fd2f'):
		print 'PROCESSING: '+str(z.zid)+' '+str(z.name)
		zpolygon = asShape(z.polygon)
		for e in elements:
			if zpolygon.intersects(e):
				print mapping(e)
				point = wave.objects(loc__geo_intersects=mapping(e)).first()
				point2 = wavedirection.objects(loc__geo_intersects=mapping(e)).first()
				data = []

				if point and point2:
					point = point['values']
					point2 = point2['values']
					data = []
					for i in range(1,366):
						if data:
							wavedirection_visualisation.objects.insert(data)
							data = []
						if str(i) in point and str(i) in point2:
							wdv = wavedirection_visualisation(zid=z.zid)
							wdv.date = datetime(year=2018, month=1, day=1)+timedelta(days=i-1)
							wdv.loc = mapping(e)
							wdv.height = point[str(i)]['0']
							wdv.direction = point2[str(i)]['0']
							data.append(wdv)
					else:
						if data:
							wavedirection_visualisation.objects.insert(data)
							data = []

if __name__ == '__main__':
	START = datetime.now()
	visualisation()
	print 'TIME: '+str(datetime.now()-START)
	print 'completed!'