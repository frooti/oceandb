import sys 
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()
import math
import numpy as np
import scipy.io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from download.models import zone, zonedata, wave, wavedirection, waveperiod, bathymetry, tide, current, currentdirection

# grid_path = '/Users/ravi/Desktop/current/uv/1_jan_current.mat'

# MAT = scipy.io.loadmat(grid_path)
# X = MAT['data']['X'][0][0]
# Y = MAT['data']['Y'][0][0]
# XVAL = MAT['data']['XComp'][0][0][0]
# YVAL = MAT['data']['YComp'][0][0][0]
# Q = plt.quiver(LNG, LAT, XVAL, YVAL)

for z in zone.objects(zid='b951a954-f3f7-44f6-80a6-0194cbee50a1'):
	print z.zid, z.name
	X = [] #np.full(X.shape, np.nan)
	Y = [] #np.full(X.shape, np.nan)
	U = [] #np.full(X.shape, np.nan)
	V = [] #np.full(X.shape, np.nan)

	# fetch data
	current_data = {}
	for c in current.objects(loc__geo_intersects=z.polygon):
		key = ','.join([str(i) for i in c.loc['coordinates']])
		value = c.values['1']['0']
		if key in current_data:
			current_data[key]['s'] = value
		else:
			 current_data[key] = {'s': value}

	for cd in currentdirection.objects(loc__geo_intersects=z.polygon):
		key = ','.join([str(i) for i in cd.loc['coordinates']])
		value = cd.values['1']['0']
		if key in current_data:
			current_data[key]['d'] = value
		else:
			current_data[key] = {'d': value}

	for d in current_data:
		x, y = [float(i) for i in d.split(',')]
		speed = current_data[d]['s']
		direction = current_data[d]['d']
		u = speed*math.cos(direction)
		v = speed*math.sin(direction)

		X.append(x)
		Y.append(y)
		U.append(u)
		V.append(v)

	plt.quiver(X, Y, U, V)
	plt.axis('off')
	plt.savefig('quiver.png', transparent=True)
