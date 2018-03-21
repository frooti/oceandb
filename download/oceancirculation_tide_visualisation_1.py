import os
import sys 
sys.stdout.flush()
import glob
import json
import gc
import numpy as np
import utm

from math import isnan

from datetime import datetime, timedelta

## CONFIG ##
file_path = '/tmp/sam_kol.dat'
output_path = 'oceancirculatin_tide_visualisation.data'
date = datetime(day=1, month=1, year=2018) # GMT
timestep = timedelta(days=0, hours=2, minutes=0)
UTM_ZONE = 45 
NODE_COUNT = 68604
ELEMENT_COUNT = 134659
## CONFIG ##

NODES = [[] for i in range(0, NODE_COUNT+1)]
ELEMENTS = [[] for i in range(0, ELEMENT_COUNT+1)]

START = datetime.now()

def visualisation():
	global date
	global START
	global NODES
	global ELEMENTS

	with open(output_path, 'a') as o:
		with open(file_path, 'r') as f:
			print 'PROCESSING: '+str(file_path)

			node = 1
			element = 1
			for line in f:
				line = line.strip().split(' ')
				if len(line)==9 or len(line)==4: # NODE
					try:
						if len(line)==9:
							line = [float(i) for i in line]
							node += 1
							lng, lat = utm.to_latlon(line[0], line[1], UTM_ZONE, 'U')
							depth = line[2]
							NODES[node] = [lng, lat, depth]
						elif len(line)==4:
							line = [float(i) for i in line]
							node += 1
							depth = line[0]
							NODES[node][2] = depth
					except Exception, e:
						print e
				elif len(line)==3: # ELEMENT
					try:
						line = [int(i) for i in line]
						element += 1
						ELEMENTS[element] = line
					except Exception, e:
						print e

				if node and node==NODE_COUNT:
					node = 0
					
					# write to ourput
					for E in ELEMENTS:
						if E:
							polygon = {'type': 'Polygon', 'coordinates': [[NODES[n][:-1] for n in E]]}
							polygon['coordinates'][0] += [polygon['coordinates'][0][0]]
							depth = round(np.mean([NODES[n][-1] for n in E]), 2)
							output_line = json.dumps(polygon)+'$$'+str(depth)+'$$'+date.isoformat()
							o.write(output_line+'\n')

					date += timestep
					if date.hour>=4:
						break

if __name__ == '__main__':
	visualisation()