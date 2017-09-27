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
	
	datapoints = 0
	try:
		polygon = json.loads(polygon)
		if data and polygon and data in ['wave', 'bathymetry']:
			if data == 'wave':
				datapoints = wave.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
			elif data == 'bathymetry':
				datapoints = bathymetry.objects(__raw__={'l':{'$geoWithin':{'$geometry': polygon}}}).count()
			res['status'] = True
			res['msg'] = 'success'
			res['price'] = '$'+str(datapoints*0.1)
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
			o.price = getPrice(data, polygon)[0]
			o.save()

			res['status'] = True
			res['msg'] = 'order placed.'
	except Exception, e:
		print e
		res['status'] = False
		res['msg'] = 'Someting went wrong.'

	return HttpResponse(json.dumps(res, default=default))