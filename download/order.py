from models import *
import csv
from datetime import datetime, timedelta
s3 = boto3.resource('s3')

def upload_file(filename, oid):
	session = boto3.Session()
	s3_client = session.client('s3')

	try:
		print "Uploading file:", filename

		tc = boto3.s3.transfer.TransferConfig()
		t = boto3.s3.transfer.S3Transfer(client=s3_client, config=tc)

		t.upload_file(filename, 'dataraftoceandb', oid)

	except Exception as e:
		print "Error uploading: %s" % ( e )

orders = order.objects(download_link=None)
for o in orders:
	with open('/home/ubuntu/projects/oceandb/download/tmp.csv', 'w') as f:
		datapoints = []

		if o.data == 'wave':
			fieldnames = ['long', 'lat', 'height']
			writer = csv.DictWriter(f, fieldnames=fieldnames)
			writer.writeheader()

			datapoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
			for d in datapoints:
				try:
					values = d.values
					for year in values:
						for day in d.values[year]):
							value = d.values[year][day]
							date = datetime(year=year, month=1, day=1)+timedelta(days=int(day)).strftime('%Y-%m-%d %H:%M')
							writer.writerow({'long': d.loc['coordinates'][0], 'lat': d.loc['coordinates'][1], 'height': value, 'date':date})
				except Exception, e:
					print e
		elif o.data == 'bathymetry':
			fieldnames = ['long', 'lat', 'depth']
			writer = csv.DictWriter(f, fieldnames=fieldnames)
			writer.writeheader()

			datapoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
			for d in datapoints:
				try:
					writer.writerow({'long': d.loc['coordinates'][0], 'lat': d.loc['coordinates'][1], 'depth': d.depth})
				except Exception, e:
					print e
		f.close()

		# publish to s3
		upload_file('/home/ubuntu/projects/oceandb/download/tmp.csv', o.oid)
		print 'https://s3-ap-southeast-1.amazonaws.com/dataraftoceandb/'+o.oid
