from models import *
import csv
from datetime import datetime, timedelta
import boto3
import time
import smtplib

ses = boto3.client('ses', region_name='us-east-1')

##### CONFIG #####
HOST = '10.24.1.151'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ravi@dataraft.in'
EMAIL_HOST_PASSWORD = 'Fr##ti36'
EMAIL_USE_TLS = True
##################

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
			with open('/var/www/dataraft.in/'+o.oid+'.csv', 'w+') as f:
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
				# upload_file('/home/ubuntu/projects/oceandb/download/tmp.csv', o.oid+'.csv')
				# download_link = 'https://s3-ap-southeast-1.amazonaws.com/dataraftoceandb/'+o.oid+'.csv'
				
				download_link = 'https://'+HOST+'/'+o.oid+'.csv'

				# email client
				# email_msg = 'Hi, \n Below is your download link:\n'+download_link+'\nThank You,\nSamudra Team.'
				# email = {
				# 	'Source': 'order@dataraft.in',
				# 	'Destination': {'ToAddresses': [o.email], 'BccAddresses': ['ravi@dataraft.in']},
				# 	'Message': {
				# 		'Subject': {'Data': 'Dataraft: Download link for your Order #'+str(o.oid)},
				# 		'Body': {'Text': {'Data': email_msg}},
				# 	},					
				# }
				# ses.send_email(**email)
				smtp = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
				smtp.starttls()
				smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
				send_from = 'ravi@dataraft.in'
				send_to = [o.email]
				send_bcc = ['ravi.muppalaneni@gmail.com']
				subject = 'Download link for your Order #'+str(o.oid)
				message = 'Hi, \n Below is your download link:\n'+download_link+'\n\nThank You,\nSamudra Team.'
				print 'email sent.'

				o.processed_at = datetime.now()
				o.download_link = download_link
				o.save()
	except Exception, e:
		print e
	time.sleep(1)
