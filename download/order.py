from models import *
import csv
from datetime import datetime, timedelta
import boto3
import time

ses = boto3.client('ses', region_name='us-east-1')

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

while True:
	try:
		orders = order.objects(processed_at=None)
		for o in orders:
			print 'processing: '+o.oid
			with open('/home/ubuntu/projects/oceandb/download/tmp.csv', 'w') as f:
				datapoints = []

				if o.data == 'wave':
					from_date = o.from_date
					to_date = o.to_date
					fieldnames = ['long', 'lat', 'height', 'date']
					writer = csv.DictWriter(f, fieldnames=fieldnames)
					writer.writeheader()

					spatialpoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
					for d in spatialpoints:
						try:
							values = d.values
							from_date = o.from_date

							while from_date<=to_date:
								day = str(from_date.timetuple().tm_yday)
								year = str(from_date.year)
								try:
									writer.writerow({'long': d.loc['coordinates'][0], 'lat': d.loc['coordinates'][1], 'height': d.values[year][day], 'date':from_date.strftime('%Y-%m-%d %H:%M')})
								except Exception, e:
									pass 
								from_date += timedelta(days=1)
						except Exception, e:
							print e
				elif o.data == 'bathymetry':
					fieldnames = ['long', 'lat', 'depth']
					writer = csv.DictWriter(f, fieldnames=fieldnames)
					writer.writeheader()

					spatialpoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
					for d in spatialpoints:
						try:
							writer.writerow({'long': d.loc['coordinates'][0], 'lat': d.loc['coordinates'][1], 'depth': d.depth})
						except Exception, e:
							pass
				f.close()

				# publish to s3
				upload_file('/home/ubuntu/projects/oceandb/download/tmp.csv', o.oid)
				download_link = 'https://s3-ap-southeast-1.amazonaws.com/dataraftoceandb/'+o.oid
				
				# email client
				email_msg = 'Hi, \n Below is your order #'+o.oid+' download link:\n'+download_link
				email = {
					'Source': 'order@dataraft.in',
					'Destination': {'ToAddresses': [o.email]},
					'Message': {
						'Subject': {'Data': 'reg: Order #'+str(o.oid)},
						'Body': {'Text': {'Data': email_msg}},
					},					
				}
				ses.send_email(**email)
				print 'email sent.'
				o.processed_at = datetime.now()
				o.download_link = download_link
				o.save()
	except Exception, e:
		print e
	time.sleep(5)
