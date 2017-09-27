from models import *

orders = order.objects(download_link=None)
for o in orders:
	data = []
	datapoints = []

	if o.data == 'wave':
		datapoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
		for d in datapoints:
			try:
				data.append(d.loc['coordinates'][0], d.loc['coordinates'][1], d.height)
			except Exception, e:
				print e
	elif o.data == 'bathymetry':	
		datapoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
		for d in datapoints:
			try:
				data.append(d.loc['coordinates'][0], d.loc['coordinates'][1], d.depth)
			except Exception, e:
				print e

	print data
