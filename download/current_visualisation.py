import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import scipy.io
from shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, current, currentdirection, current_visualisation
from datetime import datetime, timedelta

## CONFIG ##
grid_file = '/rawdata/current/jan/depth_averaged_velocity_jan_1.mat'
## CONFIG ##

MAT = scipy.io.loadmat(grid_file)
LNG = MAT['data']['X'][0][0]
LAT = MAT['data']['Y'][0][0]
GRID = MAT['data']['X'][0][0].shape

def visualisation():
	elements = []
	for i in range(0, GRID[0]):
		for j in range(0, GRID[1]):
			p = [round(float(LNG[i][j]), 3), round(float(LAT[i][j]), 3)]
			try:
				point = asShape({'type': 'Point', 'coordinates': p})
				if point.is_valid:
					elements.append(point)
			except:
				pass

	for z in zone.objects(zid='b951a954-f3f7-44f6-80a6-0194cbee50a1'):
		print 'PROCESSING: '+str(z.zid)+' '+str(z.name)
		zpolygon = asShape(z.polygon)
		for e in elements:
			if zpolygon.intersects(e):
				print mapping(e)
				point = current.objects(loc__geo_intersects=mapping(e)).first()
				point2 = currentdirection.objects(loc__geo_intersects=mapping(e)).first()

				if point and point2:
					data = []
					for i in range(1,366):
						if data:
							current_visualisation.objects.insert(data)
							data = []
						cv = current_visualisation(zid=z.zid)
						cv.date = datetime(year=2018, month=1, day=i)
						cv.loc = mapping(e)
						cv.speed = point['values'][str(i)]['0']
						cv.direction = point2['values'][str(i)]['0']
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