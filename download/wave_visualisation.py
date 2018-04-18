import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import scipy.io
from shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, wave, wavedirection, wave_visualisation
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
			if i!=GRID[0]-1 and j!=GRID[1]-1:
				p1 = [round(longitude1+(longitude_delta*j), 3), round(latitude1+(latitude_delta*i), 3)]
				p2 = [round(longitude1+(longitude_delta*(j+1)), 3), round(latitude1+(latitude_delta*i), 3)]
				p3 = [round(longitude1+(longitude_delta*(j+1)), 3), round(latitude1+(latitude_delta*(i+1)), 3)]
				p4 = [round(longitude1+(longitude_delta*j), 3), round(latitude1+(latitude_delta*(i+1)), 3)]
				try:
					polygon = asShape({'type': 'Polygon', 'coordinates': [[p1, p2, p3, p4, p1]]})
					if polygon.is_valid:
						elements.append(polygon)
				except:
					pass

	for z in zone.objects(zid='b3913413-5b23-4021-a41b-182166e9fd2f'):
		print 'PROCESSING: '+str(z.zid)+' '+str(z.name)
		zpolygon = asShape(z.polygon)
		for e in elements:
			if zpolygon.intersects(e):
				print mapping(e)
				points = [w['values'] for w in wave.objects(loc__geo_intersects=mapping(e))]
				if points:
					data = []
					for i in range(1,366):
						if data:
							wave_visualisation.objects.insert(data)
							data = []
						values = []
						for p in points:
							try:
								values.append(p[str(i)]['0'])
							except:
								pass

						if values:
							wv = wave_visualisation(zid=z.zid)
							wv.date = datetime(year=2018, month=1, day=1)+timedelta(days=i-1)
							wv.polygon = mapping(e)
							wv.height = mean(values)
							data.append(wv)
					else:
						if data:
							wave_visualisation.objects.insert(data)
							data = []

if __name__ == '__main__':
	START = datetime.now()
	visualisation()
	print 'TIME: '+str(datetime.now()-START)
	print 'completed!'
