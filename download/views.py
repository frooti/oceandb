# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import zone, order, wave, bathymetry
import boto3
from django.core.mail import EmailMultiAlternatives
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
			if data=='wave':
				spatialpoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
				available_days = 0
				sample = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}})[0]
				
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
		
		if data and polygon and data in ['wave', 'bathymetry']:
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

		if email and data and data in ['wave', 'bathymetry'] and polygon:
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