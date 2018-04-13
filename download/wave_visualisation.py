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

longitude_delta = (longitude2-longitude1)/(grid[1]-1)
latitude_delta = (latitude2-latitude1)/(grid[0]-1)

def visualisation():
	elements = []
	for i in GRID[0]:
		for j in GRID[1]:
			if i!=GRID[0]-1 and j!=GRID[1]-1:
				p1 = [round(longitude1+(longitude_delta*j), 3), round(latitude1+(latitude_delta*i), 3)]
				p2 = [round(longitude1+(longitude_delta*(j+1)), 3), round(latitude1+(latitude_delta*i), 3)]
				p3 = [round(longitude1+(longitude_delta*(j+1)), 3), round(latitude1+(latitude_delta*(i+1)), 3)]
				p4 = [round(longitude1+(longitude_delta*j), 3), round(latitude1+(latitude_delta*(i+1)), 3)]
				elements.append(asShape({'type': 'Polygon', 'coordinates': [[p1, p2, p3, p4, p1]]}))

	for z in zone.objects(zid='b951a954-f3f7-44f6-80a6-0194cbee50a1'):
		zpolygon = shape(z.polygon)
		for e in elements:
			if e.intersects(zpolygon):
				points = [w for w in wave.objects(loc__geo_intersects=mapping(e))]
				if points:
					for i in range(1,366):
						values = []
						for p in points:
							values.append(p['values'][str(i)]['0'])

						wv = wave_visualisation(zid=z.zid)
						wv.date = datetime(year=2018, month=1, day=i)
						wv.polygon = mapping(e)
						wv.height = mean(values)
						wv.save()

if __name__ == '__main__':
	visualisation()