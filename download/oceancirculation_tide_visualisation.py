import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

import utm
from shapely.geometry import asShape, mapping
from statistics import mean
from download.models import zone, tide, tide_visualisation
from datetime import datetime, timedelta

## CONFIG ##
grid_file = '/tmp/kk.dat'
zid = ''
UTM_ZONE = 45 
NODE_COUNT = 68604
ELEMENT_COUNT = 134659
## CONFIG ##

NODES = [[] for i in range(0, NODE_COUNT+1)]
ELEMENTS = [[] for i in range(0, ELEMENT_COUNT+1)]

def visualisation():
	elements = []
	with open(grid_file, 'r') as f:
		print 'POPULATING ELEMENTS ...'

		node = 0
		element = 0
		for line in f:
			line = line.strip().split(' ')
			if len(line)==9 or len(line)==4: # NODE
				try:
					if len(line)==9:
						line = [float(i) for i in line]
						node += 1
						lat, lng = utm.to_latlon(line[0], line[1], UTM_ZONE, 'U')
						NODES[node] = [lng, lat]
				except Exception, e:
					print e
			elif len(line)==3: # ELEMENT
				try:
					line = [int(i) for i in line]
					element += 1
					ELEMENTS[element] = line
				except Exception, e:
					print e

			if element==ELEMENT_COUNT and node==NODE_COUNT:
				for E in ELEMENTS:
					if E:
						polygon = {'type': 'Polygon', 'coordinates': [[NODES[n][:-1] for n in E]]}
						try:
							polygon = asShape(polygon)
							if polygon.is_valid:
								elements.append(polygon)
						except:
							pass
				
				print 'ELEMENTS: '+str(len(elements))
				break

	for z in zone.objects(ztype='project', zid=zid):
		print 'PROCESSING: '+str(z.zid)+' '+str(z.name)
		zpolygon = asShape(z.polygon)
		for e in elements:
			if zpolygon.intersects(e):
				print mapping(e)
				points = [t['values'] for t in tide.objects(zid=zid, loc__geo_intersects=mapping(e))]
				
				if points:
					data = []
					for i in range(1,366):
						if data:
							tide_visualisation.objects.insert(data)
							data = []
						values = []
						for p in points:
							try:
								values.append(p[str(i)]['0'])
							except:
								pass

						if values:
							tv = tide_visualisation(zid=z.zid)
							tv.date = datetime(year=2018, month=1, day=1)+timedelta(days=i-1)
							tv.polygon = mapping(e)
							tv.depth = mean(values)
							data.append(tv)
					else:
						if data:
							tide_visualisation.objects.insert(data)
							data = []

if __name__ == '__main__':
	START = datetime.now()
	visualisation()
	print 'TIME: '+str(datetime.now()-START)
	print 'completed!'