# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import zone, userzone, order, wave, wavedirection, waveperiod, bathymetry, userbathymetry
import boto3
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from oceandb.auth import User

# Create your views here.
DEFAULT_RESPONSE = '{"status":false, "msg": "bad request."}'

from django.http import HttpResponse, HttpResponseRedirect
import django.contrib.auth as auth
import json
import uuid
import time
from datetime import datetime, timedelta
import dateutil.parser
from decimal import Decimal
import csv
from scipy.spatial import ConvexHull

ses = boto3.client('ses', region_name='us-east-1')

# utilities
def default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

MIN_PRICE = 1000
WAVE_DATAPOINT_PRICE = 1
BATHY_DATAPOINT_PRICE = 1

def login(request):
	res = json.loads(DEFAULT_RESPONSE)
	## session check ##
	if request.user:
		res['msg'] = 'session active.'
		res['status'] = True
		res['data'] = {'email': request.user.email, 'subscription_type': request.user.subscription_type, 'subscription_zones': request.user.subscription_zones, 'is_active': request.user.is_active}
		# userzones
		res['data']['userzones'] = [[uz.uzid, uz.polygon] for uz in userzone.objects(email=request.user.email)]
		return HttpResponse(json.dumps(res, default=default))

	## jugaad ##
	if '_auth_user_id' in request.session:
		request.session.pop('_auth_user_id')

	email = request.GET.get('email', '')
	password = request.GET.get('password', '')

	user = auth.authenticate(request=request, username=email, password=password)
	if user:
		auth.login(request, user)
		res['msg'] = 'login successful.'
		res['status'] = True
		res['data'] = {'email': email, 'subscription_type': user.subscription_type, 'subscription_zones': user.subscription_zones, 'is_active':user.is_active}
		# userzones
		res['data']['userzones'] = [[uz.uzid, uz.polygon] for uz in userzone.objects(email=request.user.email)]
	else:
		res['msg'] = 'email/password does not match.'
		res['status'] = False
	return HttpResponse(json.dumps(res, default=default))

def logout(request):
	res = json.loads(DEFAULT_RESPONSE)
	auth.logout(request)
	res['msg'] = 'logout successful'
	res['status'] = True
	return HttpResponse(json.dumps(res, default=default))

def signup(request):
	res = json.loads(DEFAULT_RESPONSE)
	email = request.GET.get('email', None)
	password = request.GET.get('password', None)
	organization = request.GET.get('organization', None)
	phone = request.GET.get('phone', None)
	name = request.GET.get('name', None)
	subscription_zones = request.GET.get('subscription_zones', '[]')
	subscription_type = request.GET.get('subscription_type', None)

	if email and password and organization and phone and name and subscription_type:
		try:
			if User.objects(email=email).first():
				res['status'] = False
				res['msg'] = 'email already exists.'
			else:
				if subscription_zones:
					subscription_zones = json.loads(subscription_zones)
				if subscription_type not in ['A', 'B']:
					subscription_type = 'A'
				user = User().create_user(email=email, password=password, organization=organization, phone=phone, name=name, subscription_zones=subscription_zones, subscription_type=subscription_type, subscription_date=datetime.now())
				res['status'] = True
				res['msg'] = 'user registered.'
		except Exception, e:
			print e
			res['status'] = False
			res['msg'] = 'someting went wrong.'
	else:
		res['status'] = False
		res['msg'] = 'Please fill all the form fields.'

	return HttpResponse(json.dumps(res, default=default))

def getZone(request):
	res = json.loads(DEFAULT_RESPONSE)
	try:
		zones = []
		bathymetry = []

		for z in zone.objects():
			if z.ztype == 'zone':
				zones.append({'type':'Feature', 'properties':{'zid':z.zid, 'name':z.name}, 'geometry':z.polygon})
			elif z.ztype == 'bathymetry':
				bathymetry.append({'type':'Feature', 'properties':{'zid':z.zid, 'name':z.name}, 'geometry':z.polygon})

		res['zones'] = zones
		res['bathymetry'] = bathymetry
		res['status'] = True
		res['msg'] = 'success' 
	except Exception,e:
		print e
		res['status'] = False
		res['msg'] = 'Someting went wrong.'

	return HttpResponse(json.dumps(res, default=default))


def getPrice(data, polygon, from_date, to_date):
	datapoints = 0
	if data and polygon and from_date and to_date:
		try:
			if data in ['wave', 'waveperiod', 'wavedirection']:
				if data=='wave':
					model = wave
				elif data=='wavedirection':
					model = wavedirection
				else:
					model = waveperiod

				spatialpoints = model.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
				available_days = 0
				sample = model.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}})[0]
				
				while from_date<=to_date:
					day = str(from_date.timetuple().tm_yday)
					year = str(from_date.year)
					try:
						sample.values[year][day]
						available_days += 1
					except:
						pass
					from_date += timedelta(days=1)

				datapoints = spatialpoints*available_days
				price = 0

				if datapoints:
					price = round(MIN_PRICE+(datapoints*WAVE_DATAPOINT_PRICE), 0)
				else:
					price = 0
				return price, datapoints
			elif data == 'bathymetry':
				datapoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
				price = 0

				if datapoints:
					price = round(MIN_PRICE+(datapoints*BATHY_DATAPOINT_PRICE), 0)
				else:
					price = 0
				return price, datapoints
		except:
			pass
	return -1, 0

def fetchPrice(request):
	res = json.loads(DEFAULT_RESPONSE)
	polygon = request.GET.get('polygon', None)
	data =  request.GET.get('data', None)
	from_date = request.GET.get('from_date', None)
	to_date = request.GET.get('to_date', None)
	try:
		from_date = dateutil.parser.parse(from_date)
		to_date = dateutil.parser.parse(to_date)
	except:
		from_date = dateutil.parser.parse((datetime.now()-timedelta(days=7)).isoformat())
		to_date = dateutil.parser.parse((datetime.now()+timedelta(days=7)).isoformat())
	user = request.user
	datapoints = 0
	try:
		polygon = json.loads(polygon)
		
		if polygon and data in ['wave', 'wavedirection', 'waveperiod', 'bathymetry']:
			price, datapoints = getPrice(data, polygon, from_date, to_date)

			res['status'] = True
			res['msg'] = 'success'
			res['datapoints'] = datapoints
			if price>=0:
				res['price'] = '$'+str(price)
			else:
				res['price'] = '$0'
			res['size'] = str(datapoints*34/1024)+' KB'
			if request.user:
				res['email'] = request.user.email
	except Exception, e:
		print e
		res['status'] = False
		res['msg'] = 'Someting went wrong.'

	return HttpResponse(json.dumps(res, default=default))

def orderData(request):
	res = json.loads(DEFAULT_RESPONSE)
	polygon = request.GET.get('polygon', None)
	data =  request.GET.get('data', None)
	from_date = request.GET.get('from_date', (datetime(day=1, month=9, year=2017)-timedelta(days=7)).isoformat())
	to_date = request.GET.get('to_date', (datetime(day=1, month=9, year=2017)+timedelta(days=7)).isoformat())
	user = request.user
	email = user.email if user else None
	#organization = request.GET.get('organization', None)

	try:
		polygon = json.loads(polygon)
		from_date = dateutil.parser.parse(from_date)
		to_date = dateutil.parser.parse(to_date)

		if email and polygon and data in ['wave', 'wavedirection', 'waveperiod', 'bathymetry']:
			o = order(oid=str(uuid.uuid4()))
			o.email = user.email
			o.data = data
			o.polygon = polygon
			o.from_date = from_date
			o.to_date = to_date
			price, datapoints = getPrice(data, polygon, from_date, to_date)
			if datapoints>0:
				o.price = price
				o.datapoints = datapoints
				o.save()

				res['status'] = True
				res['msg'] = 'order placed.'

				# email
				if 'test' not in o.email:
					sub = 'Received Order #'+str(o.oid)
					email_msg = 'Hi, \n We are processing your download request. You will receive the download link within 1 hr. \n\nThank You,\nSamudra Team.'
					from_email = 'ravi@dataraft.in'
					to_email = [o.email]
					cc = ['ravi@dataraft.in']
					msg = EmailMultiAlternatives(sub, email_msg, from_email, to_email, cc=cc)
					msg.send()
	except Exception, e:
		print e
		res['status'] = False
		res['msg'] = 'Someting went wrong.'

	return HttpResponse(json.dumps(res, default=default))

def heatMap(request):
	res = json.loads(DEFAULT_RESPONSE)
	timestep = request.GET.get('timestep', '1')

	try:
		f = open('/home/ubuntu/projects/oceandb/download/timestep/timestep'+timestep+'.json')
		res['data'] = f.read()
		res['status'] = True
		res['msg'] = 'success' 
	except Exception,e:
		print e
		res['status'] = False
		res['msg'] = 'Someting went wrong.'

	return HttpResponse(json.dumps(res, default=default))

@csrf_exempt
def uploadData(request):
	res = json.loads(DEFAULT_RESPONSE)
	if request.user:
		f = request.FILES.get('csv-file')
		name = request.POST.get('name', None)
		if f and name:
			try:
				if userzone.objects(email=request.user.email, name=name).first(): # unique name check
					res['msg'] = name+' '+'already exists. Please provide a unique zone name.'
					res['status'] = False
					return HttpResponse(json.dumps(res, default=default))
				
				points = []
				points_geojson = []
				for row in csv.reader(f.read().splitlines()):
					try:
						# remove empty cells
						for i, r in enumerate(row):
							row[i] = r.strip()
						for i in range(len(row)):
							if '' in row:
								row.remove('')
						if len(row)!=3:
							continue

						longitude = float(row[1])
						latitude = float(row[0])
						value = float(row[2])
						point = [longitude, latitude]
						points.append(point)
						points_geojson.append([{'type': 'Point', 'coordinates': point}, value])
					except Exception, e:
						res['msg'] = 'There is problem with your data. Please correct it and try again.'
						res['status'] = False
						return HttpResponse(json.dumps(res, default=default))
					
				chull = []
				try: # chull check
					hull = ConvexHull(points)
					for i in hull.vertices:
						chull.append(points[i])
					chull = chull+[chull[0]]
					if not chull:
						res['msg'] = 'Your data does not have a polygon boundary. Please correct it and try again.'
						res['status'] = False
						return HttpResponse(json.dumps(res, default=default))
				except Exception, e:
					res['msg'] = 'Your data does not have a polygon boundary. Please correct it and try again.'
					res['status'] = False
					return HttpResponse(json.dumps(res, default=default))

				# subscribed zone check
				intersection_zones = [z.zid for z in zone.objects(polygon__geo_intersects=[chull], ztype='zone')]
				subscribed_zones = request.user.subscription_zones
				if not intersection_zones or list(set(intersection_zones)-set(subscribed_zones)):
					res['msg'] = 'Some of your data is outside your subscribed zone. Please correct it and try again.'
					res['status'] = False
					return HttpResponse(json.dumps(res, default=default))

				# add to database
				uz = userzone(uzid=str(uuid.uuid4()))
				uz.email = request.user.email
				uz.name = name
				uz.ztype = 'bathymetry'
				uz.polygon = {'type':'Polygon', 'coordinates': [chull]}
				uz.save()

				data = []
				for p in points_geojson:
					data.append(userbathymetry(loc=p[0], depth=p[1], email=request.user.email, uzid=uz.uzid))
				if data:
					userbathymetry.objects.insert(data)
				
				res['msg'] = 'Data uploaded successfully.'
				res['status'] = True
				return HttpResponse(json.dumps(res, default=default))
			except Exception, e:
				print e
				res['msg'] = 'Something went wrong.'
				res['status'] = False
	return HttpResponse(json.dumps(res, default=default))

def pointData(request):
	res = json.loads(DEFAULT_RESPONSE)
	point = request.GET.get('point', None)
	data =  request.GET.get('data', None)
	user = request.user
	from_date = datetime.now()
	to_date = datetime.now()+timedelta(days=14)

	try:
		point = json.loads(point)

		if request.zone and point and data in ['wave', 'bathymetry']:
			intersection_zones = [z.zid for z in zone.objects(polygon__geo_intersects=point, ztype='zone')]
			subscribed_zones = request.user.subscription_zones
			
			if intersection_zones and not list(set(intersection_zones)-set(subscribed_zones)): # subscribed zone check
				if data=='wave':
					data = []
					p = wave.objects(loc__near=point).first()
					if p:
						while from_date<=to_date:
							p.values
							day = str(from_date.timetuple().tm_yday)
							year = str(from_date.year)
							try:
								row = {}
								row['long'] = p.loc['coordinates'][0]
								row['lat'] = p.loc['coordinates'][1]
								row['date'] = from_date.strftime('%Y-%m-%d')
								row['param'] = p.values[year][day]
								data.append(row)
							except:
								pass
							from_date += timedelta(days=1)
					res['status'] = True
					res['msg'] = 'success'
					res['data'] = data

				elif data=='bathymetry':
					data = []
					p = bathymetry.objects(loc__near=point).first()
					if p:
						try:
							row = {}
							row['long'] = p.loc['coordinates'][0]
							row['lat'] = p.loc['coordinates'][1]
							row['param'] = p.depth
							data.append(row)
						except:
							pass
					res['status'] = True
					res['msg'] = 'success'
					res['data'] = data
	except Exception, e:
		print e
		res['status'] = False
		res['msg'] = 'Someting went wrong.'

	return HttpResponse(json.dumps(res, default=default))
