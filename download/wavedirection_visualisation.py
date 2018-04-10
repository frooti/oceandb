import scipy.io
import shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, wave, wavedirection, wavedirection_visualisation
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
			p = [round(longitude1+(longitude_delta*j), 3), round(latitude1+(latitude_delta*i), 3)]
			elements.append(asShape({'type': 'Point', 'coordinates': p}))

	for z in zone.objects(zid='b951a954-f3f7-44f6-80a6-0194cbee50a1'):
		zpolygon = shape(z.polygon)
		for e in elements:
			if e.intersects(zpolygon):
				point = wave.objects(loc__geo_intersects=mapping(e)).first()
				point2 = wavedirection.objects(loc__geo_intersects=mapping(e)).first()
				
				for i in range(1,366):
					wdv = wavedirection_visualisation(zid=z.zid)
					wdv.date = datetime(year=2018, month=1, day=i)
					wdv.loc = mapping(e)
					wdv.height = point['values'][str(i)]['0']
					wdv.direction = point2['values'][str(i)]['0']
					wdv.save()

if __name__ == '__main__':
	visualisation()