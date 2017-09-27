from models import *
import csv

orders = order.objects(download_link=None)
for o in orders:
	with open('tmp.csv', 'w') as f:
		datapoints = []

		if o.data == 'wave':
			fieldnames = ['long', 'lat', 'height']
    		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    		writer.writeheader()

			datapoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
			for d in datapoints:
				try:
					writer.writerow({'long': d.loc['coordinates'][0], 'lat': d.loc['coordinates'][1], 'height': d.height})
				except Exception, e:
					print e
		elif o.data == 'bathymetry':
			fieldnames = ['long', 'lat', 'depth']
    		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    		writer.writeheader()

			datapoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
			for d in datapoints:
				try:
					writer.writerow({'long': d.loc['coordinates'][0], 'lat': d.loc['coordinates'][1], 'depth': d.depth})
				except Exception, e:
					print e
