# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import order, wave, bathymetry

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
	email = request.GET.get('email', '')
	password = request.GET.get('password', '')

	user = auth.authenticate(request=request, username=email, password=password)
	if user:
		auth.login(request, user)
		res['msg'] = 'login successful.'
		res['status'] = True
		res['data'] = {'email': email}
	else:
		res['msg'] = 'email/password does not match.'
		res['status'] = False
	return HttpResponse(json.dumps(res, default=default))
 
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/')


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
					price = (round(MIN_PRICE+(datapoints*WAVE_DATAPOINT_PRICE), 0), datapoints)
				else:
					price = (0, 0)
				return price, datapoints
			elif dtype == 'bathymetry':
				datapoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
				price = 0

				if datapoints:
					price = (round(MIN_PRICE+(datapoints*BATHY_DATAPOINT_PRICE), 0), datapoints)
				else:
					price = (0, 0)
				return price, datapoints
		except:
			pass
	return -1, 0

def fetchPrice(request):
	res = json.loads(DEFAULT_RESPONSE)
	polygon = request.GET.get('polygon', None)
	data =  request.GET.get('data', None)
	from_date = request.GET.get('from_date', (datetime(day=1, month=9, year=2017)-timedelta(days=7)).isoformat())
	to_date = request.GET.get('to_date', (datetime(day=1, month=9, year=2017)+timedelta(days=7)).isoformat())
	
	datapoints = 0
	try:
		from_date = dateutil.parser.parse(from_date)
		to_date = dateutil.parser.parse(to_date)
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
	email = request.GET.get('email', None)
	organization = request.GET.get('organization', None)

	try:
		polygon = json.loads(polygon)
		from_date = dateutil.parser.parse(from_date)
		to_date = dateutil.parser.parse(to_date)

		if data and data in ['wave', 'bathymetry'] and polygon and email and organization:
			o = order(oid=str(uuid.uuid4()))
			o.data = data
			o.polygon = polygon
			o.from_date = from_date
			o.to_date = to_date
			o.organization = organization
			o.email = email
			price = getPrice(data, polygon, from_date, to_date)[0]
			if price:
				o.price = price 
				o.save()

				res['status'] = True
				res['msg'] = 'order placed.'
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