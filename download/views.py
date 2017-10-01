# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import order, wave, bathymetry

# Create your views here.
DEFAULT_RESPONSE = '{"status":false, "msg": "bad request."}'

from django.http import HttpResponse
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

def fetchPrice(request):
	res = json.loads(DEFAULT_RESPONSE)
	polygon = request.GET.get('polygon', None)
	data =  request.GET.get('data', None)
	from_date = request.GET.get('from_date', (datetime.utcnow()-timedelta(days=7)).isoformat())
	to_date = request.GET.get('to_date', (datetime.utcnow()+timedelta(days=7)).isoformat())
	
	datapoints = 0
	try:
		from_date = dateutil.parser.parse(from_date)
		to_date = dateutil.parser.parse(to_date)
		polygon = json.loads(polygon)
		
		if data and polygon and data in ['wave', 'bathymetry']:
			if data == 'wave':
				spatialpoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
				available_days = 0
				sample = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}})[0]
				
				check_days = []
				while from_date<=to_date:
					check_days.append([from_date.timetuple().tm_yday, from_date.year])
					from_date += timedelta(days=1)

				for d in check_days:
					try:
						sample.values[d[1]][d[0]]
						available_days += 1
					except:
						pass
				datapoints = spatialpoints*available_days
				res['status'] = True
				res['msg'] = 'success'
				res['datapoints'] = datapoints
				res['price'] = '$'+str(max(datapoints*0.1, 1500))
				
				res['size'] = str(datapoints*20/1024)+' KB'
			elif data == 'bathymetry':
				datapoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
				res['status'] = True
				res['msg'] = 'success'
				res['price'] = '$'+str(max(datapoints*0.1, 1500))
				res['datapoints'] = datapoints
				res['size'] = str(datapoints*20/1024)+' KB'
	except Exception, e:
		print e
		res['status'] = False
		res['msg'] = 'Someting went wrong.'

	return HttpResponse(json.dumps(res, default=default))

def getPrice(data, polygon):
	datapoints = 0
	if data and polygon:
		try:
			if data=='wave':
				datapoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
				return datapoints*0.1, datapoints
			elif dtype == 'bathymetry':
				datapoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
				return datapoints*0.1, datapoints
		except:
			pass
	return -1, 0

def orderData(request):
	res = json.loads(DEFAULT_RESPONSE)
	polygon = request.GET.get('polygon', None)
	data =  request.GET.get('data', None)
	email = request.GET.get('email', None)
	organization = request.GET.get('organization', None)

	try:
		polygon = json.loads(polygon)
		if data and data in ['wave', 'bathymetry'] and polygon and email and organization:
			o = order(oid=str(uuid.uuid4()))
			o.data = data
			o.polygon = polygon
			o.organization = organization
			o.email = email
			price = getPrice(data, polygon)[0]
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