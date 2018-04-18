import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, wave, bathymetry_visualisation
from datetime import datetime, timedelta
from astropy.coordinates import Angle

## CONFIG ##
GRID = (9600, 10800) 
latitude1, longitude1 = (108000, 108030)
latitude2, longitude2 = (-180000, 432030)
## CONFIG ##

longitude_delta = 30
latitude_delta = 30

def visualisation():
	elements = []
	for i in range(0, GRID[0]):
		for j in range(0, GRID[1]):
			if i!=GRID[0]-1 and j!=GRID[1]-1:
				p1 = [round(Angle(str(longitude1+(longitude_delta*j))+'s').degree, 10), round(Angle(str(latitude1+(latitude_delta*i))+'s').degree, 10)]
				p2 = [round(Angle(str(longitude1+(longitude_delta*(j+1)))+'s').degree, 10), round(Angle(str(latitude1+(latitude_delta*i))+'s').degree, 10)]
				p3 = [round(Angle(str(longitude1+(longitude_delta*(j+1)))+'s').degree, 10), round(Angle(str(latitude1+(latitude_delta*(i+1)))+'s').degree, 10)]
				p4 = [round(Angle(str(longitude1+(longitude_delta*j))+'s').degree, 10), round(Angle(str(latitude1+(latitude_delta*(i+1)))+'s').degree, 10)]
				try:
					polygon = asShape({'type': 'Polygon', 'coordinates': [[p1, p2, p3, p4, p1]]})
					if polygon.is_valid:
						elements.append(polygon)
				except:
					pass

	for z in zone.objects(zid='b3913413-5b23-4021-a41b-182166e9fd2f'):
		print 'PROCESSING: '+str(z.zid)+' '+str(z.name)
		zpolygon = asShape(z.polygon)
		
		data = []
		for e in elements:
			if data and len(data)%1000==0:
				bathymetry_visualisation.objects.insert(data)
				data = []

			if zpolygon.intersects(e):
				print mapping(e)
				points = [b['values'] for b in bathymetry.objects(loc__geo_intersects=mapping(e))]
				
				if points:
					values = []
					for p in points:
						values.append(p.depth)

					bv = bathymetry_visualisation(zid=z.zid)
					bv.polygon = mapping(e)
					bv.depth = mean(values)
					data.append(bv)
		else:
			if data:
				bathymetry_visualisation.objects.insert(data)
				data = []

if __name__ == '__main__':
	START = datetime.now()
	visualisation()
	print 'TIME: '+str(datetime.now()-START)
	print 'completed!'