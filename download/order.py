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

def send_email(from_addr, to_addr_list, cc_addr_list, bcc_addr_list, subject, message, login, password, smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Bcc: %s\n' % ','.join(bcc_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems


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

				if o.data in ['wave', 'wavedirection', 'waveperiod']:
					from_date = o.from_date
					to_date = o.to_date
					if o.data=='wave':
						model = wave
						param = 'height'
					elif o.data=='wavedirection':
						model = wavedirection
						param = 'direction'
					else:
						model = waveperiod
						param = 'period'
					fieldnames = ['long', 'lat', param, 'date']
					writer = csv.DictWriter(f, fieldnames=fieldnames)
					writer.writeheader()
					
					spatialpoints = model.objects(__raw__={'l':{'$geoWithin':{'$geometry':o.polygon}}})
					for d in spatialpoints:
						try:
							values = d.values
							from_date = o.from_date

							while from_date<=to_date:
								day = str(from_date.timetuple().tm_yday)
								year = str(from_date.year)
								try:
									row = {}
									row['long'] = d.loc['coordinates'][0]
									row['lat'] = d.loc['coordinates'][1]
									row['date'] = from_date.strftime('%Y-%m-%d %H:%M')
									row[param] = d.values[year][day]
									writer.writerow(row)
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
				
				download_link = 'http://'+HOST+'/'+o.oid+'.csv'

				# email client
				if 'test' not in o.email:
					email_msg = 'Hi, \n Below is your download link:\n'+download_link+'\nThank You,\nSamudra Team.'
					email = {
						'Source': 'order@dataraft.in',
						'Destination': {'ToAddresses': [o.email], 'BccAddresses': ['ravi@dataraft.in']},
						'Message': {
							'Subject': {'Data': 'Dataraft: Download link for your Order #'+str(o.oid)},
							'Body': {'Text': {'Data': email_msg}},
						},					
					}
					ses.send_email(**email)
				
				# if 'test' not in o.email:
				# 	send_from = 'ravi@dataraft.in'
				# 	send_to = [o.email]
				# 	send_cc = ['ravi@dataraft.in']
				# 	subject = 'Download link for your Order #'+str(o.oid)
				# 	message = 'Hi, \n Below is your download link:\n'+download_link+'\n\nThank You,\nSamudra Team.'
				# 	send_email(send_from, send_to, send_cc, [], subject, message, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_HOST+':'+str(EMAIL_PORT))
				# 	print 'email sent.'

				o.processed_at = datetime.now()
				o.download_link = download_link
				o.save()
	except Exception, e:
		print e
	time.sleep(1)
