import shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, wave, bathymetry_visualisation
from datetime import datetime, timedelta
from astropy.coordinates import Angle

## CONFIG ##
GRID = (9600, 10,800) 
latitude1, longitude1 = (108000, 108030)
latitude2, longitude2 = (-180000, 432030)
## CONFIG ##

longitude_delta = 30
latitude_delta = 30

def visualisation():
	elements = []
	for i in GRID[0]:
		for j in GRID[1]:
			if i!=GRID[0]-1 and j!=GRID[1]-1:
				p1 = [round(Angle(longitude1+(longitude_delta*j)).degree, 10), round(Angle(latitude1+(latitude_delta*i)).degree, 10)]
				p2 = [round(Angle(longitude1+(longitude_delta*(j+1))).degree, 10), round(Angle(latitude1+(latitude_delta*i)).degree, 10)]
				p3 = [round(Angle(longitude1+(longitude_delta*(j+1))).degree, 10), round(Angle(latitude1+(latitude_delta*(i+1))).degree, 10)]
				p4 = [round(Angle(longitude1+(longitude_delta*j)).degree, 10), round(Angle(latitude1+(latitude_delta*(i+1))).degree, 10)]

				elements.append(asShape({'type': 'Polygon', 'coordinates': [[p1, p2, p3, p4, p1]]}))

	for z in zone.objects(zid='b951a954-f3f7-44f6-80a6-0194cbee50a1'):
		zpolygon = shape(z.polygon)
		for e in elements:
			if e.intersects(zpolygon):
				points = [b for b in bathymetry.objects(loc__geo_intersects=mapping(e))]
				
				values = []
				for p in points:
					values.append(p.depth)

				bv = wave_visualisation(zid=z.zid)
				bv.polygon = mapping(e)
				bv.depth = mean(values)
				bv.save()

if __name__ == '__main__':
	visualisation()