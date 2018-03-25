import os
import sys 
sys.stdout.flush()
import glob
import json
import gc
import numpy as np
import utm

import math
from math import isnan

from datetime import datetime, timedelta

## CONFIG ##
file_path = '/tmp/kk.dat'
output_path = 'oceancirculation_current_visualisation.data'
date = datetime(day=1, month=1, year=2018) # GMT
timestep = timedelta(days=0, hours=2, minutes=0)
UTM_ZONE = 45 
NODE_COUNT = 68604
ELEMENT_COUNT = 134659
## CONFIG ##

NODES = [[] for i in range(0, NODE_COUNT+1)]

START = datetime.now()

def visualisation():
	global date
	global START
	global NODES
	
	with open(output_path, 'a') as o:
		with open(file_path, 'r') as f:
			print 'PROCESSING: '+str(file_path)

			node = 0
			for line in f:
				line = line.strip().split(' ')
				if len(line)==9 or len(line)==4: # NODE
					try:
						if len(line)==9:
							line = [float(i) for i in line]
							node += 1
							lat, lng = utm.to_latlon(line[0], line[1], UTM_ZONE, 'U')
							u, v = line[3], line[4]
							speed = math.sqrt(u**2+v**2)
							direction = round(math.degrees(math.atan2(v, u)), 2)
							# Nautical convention
							if direction>0 and direction<=90:
								direction = 90-direction
							elif direction>90 and direction<=180:
								direction = 450-direction
							elif direction>-90 and direction<=0:
								direction = 90+math.abs(direction)
							elif direction>-180 and direction<=-90:
								 direction = 90+math.abs(direction)

							NODES[node] = [lng, lat, speed, direction]
						elif len(line)==4:
							line = [float(i) for i in line]
							node += 1
							u, v = line[1], line[2]
							speed = math.sqrt(u^2+v^2)
							direction = round(math.degrees(math.atan2(v, u)), 2)
							# Nautical convention
							if direction>0 and direction<=90:
								direction = 90-direction
							elif direction>90 and direction<=180:
								direction = 450-direction
							elif direction>-90 and direction<=0:
								direction = 90+math.abs(direction)
							elif direction>-180 and direction<=-90:
								 direction = 90+math.abs(direction)
							NODES[node][2] = speed
							NODES[node][3] = direction
					except Exception, e:
						print e
				
				if node==NODE_COUNT:
					node = 0
					
					if date.hour==0:
						# write to ourput
						for n in NODES:
							if n:
								point = {'type': 'Point', 'coordinates': n[:-2]}
								speed = n[2]
								direction = n[3]
								output_line = json.dumps(point)+'$$'+str(speed)+'$$'+str(direction)+'$$'+date.isoformat()
								o.write(output_line+'\n')

					date += timestep

if __name__ == '__main__':
	visualisation()