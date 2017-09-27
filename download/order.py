from models import *
import csv
import boto3
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
	with open('tmp.csv', 'r+') as f:
		datapoints = []

		if o.data == 'wave':
			fieldnames = ['long', 'lat', 'height']
			writer = csv.DictWriter(f, fieldnames=fieldnames)
			writer.writeheader()

			datapoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
			for d in datapoints:
				try:
					writer.writerow({'long': d.loc['coordinates'][0], 'lat': d.loc['coordinates'][1], 'height': d.height})
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

		# publish to s3
		