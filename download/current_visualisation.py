import scipy.io
import shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, current, currentdirection, current_visualisation
from datetime import datetime, timedelta

## CONFIG ##
grid_file = 'current/uv/1.5_jan_current.mat'
## CONFIG ##

MAT = scipy.io.loadmat(grid_file)
LNG = MAT['data']['X'][0][0]
LAT = MAT['data']['Y'][0][0]
GRID = MAT['data']['X'][0][0].shape

def visualisation():
	elements = []
	for i in GRID[0]:
		for j in GRID[1]:
			p = [round(float(LNG[i][j]), 3), round(float(LAT[i][j]), 3)]
			elements.append(asShape({'type': 'Point', 'coordinates': p}))

	for z in zone.objects(zid='b951a954-f3f7-44f6-80a6-0194cbee50a1'):
		zpolygon = shape(z.polygon)
		for e in elements:
			if e.intersects(zpolygon):
				point = current.objects(loc__geo_intersects=mapping(e)).first()
				point2 = currentdirection.objects(loc__geo_intersects=mapping(e)).first()

				if point and point2:
					for i in range(1,366):
						cv = current_visualisation(zid=z.zid)
						cv.date = datetime(year=2018, month=1, day=i)
						cv.loc = mapping(e)
						cv.speed = point['values'][str(i)]['0']
						cv.direction = point2['values'][str(i)]['0']
						cv.save()

if __name__ == '__main__':
	visualisation()