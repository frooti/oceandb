# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from mongoengine import *
from datetime import datetime

db = connect('ocean', host='mongodb://localhost:27017/ocean', username='ocean', password='@cean99')
db["ocean"].authenticate("ocean", password="@cean99")

class zone(Document):
	zid = StringField(db_field='zid', max_length=50, required=True)
	email = StringField(db_field='e', max_length=200, required=True)
	name = StringField(db_field='name', max_length=100, required=True)
	ztype = StringField(db_field='zt', max_length=100, required= True)
	polygon = PolygonField(db_field='pl', auto_index=True, required=True)
	triangles = ListField(db_field='tr', default=[])
	date = DateTimeField(db_field='dt', default=datetime.now)
	created_at = DateTimeField(db_field='ct', default=datetime.now)

class zonedata(Document):
	zid = StringField(db_field='zid', max_length=50, required=True)
	month = IntField(db_field='m', required=True)
	triangles = ListField(db_field='tr', required=True)
	meta = {
        'indexes': [[("zid", 1), ("month", 1)]]
    }

class userzone(Document):
	uzid = StringField(db_field='uzid', max_length=50, required=True)
	email = StringField(db_field='e', max_length=200, required=True)
	name = StringField(db_field='name', max_length=100, required=True)
	ztype = StringField(db_field='zt', max_length=100, required= True)
	polygon = PolygonField(db_field='pl', auto_index=True, required=True)
	triangles = ListField(db_field='tr', default=[])
	date = DateTimeField(db_field='dt', default=datetime.now)
	created_at = DateTimeField(db_field='ct', default=datetime.now)

class order(Document):
	oid = StringField(db_field='oid', max_length=50, required=True)
	email = StringField(db_field='e', max_length=200, required=True)
	#organization = StringField(db_field='o', max_length=200, required=True)
	polygon = PolygonField(db_field='pl', auto_index=True, required=True)
	data = StringField(db_field='d', max_length=50, required=True)
	month = StringField(db_field='m', required=True)
	# from_date = DateTimeField(db_field='fd', default=None)
	# to_date = DateTimeField(db_field='td', default=None)
	price = DecimalField(db_field='p', precision=2, rounding='ROUND_HALF_UP', required=True)
	datapoints = IntField(db_field='dp', required=True)
	#payment_status = BooleanField(db_field='ps', default=False)
	download_link = StringField(db_field='dl', default=None)
	email_sent = BooleanField(db_field='em', default=False)
	created_at = DateTimeField(db_field='ct', default=datetime.now)
	processed_at = DateTimeField(db_field='pt', default=None)

class wave(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	values = DictField()

class wavedirection(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	values = DictField()

class waveperiod(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	values = DictField()

class wave_visualisation(Document):
	zid = StringField(db_field='zid', max_length=50, required=True)
	polygon = PolygonField(db_field='pl', required=True)
	date = DateTimeField(db_field='dt', required=True)
	height = FloatField(db_field='d', required=True)
	# meta = {
 #        'indexes': [[("pl", "2dsphere"), ("zid", 1), ("dt", 1)]]
 #    }

class wavedirection_visualisation(Document):
	zid = StringField(db_field='zid', max_length=50, required=True)
	loc =  PointField(db_field='l', required=True)
	date = DateTimeField(db_field='dt', required=True)
	height = FloatField(db_field='h', required=True)
	direction = FloatField(db_field='d', required=True)
	# meta = {
 #        'indexes': [[("l", "2dsphere"), ("zid", 1), ("dt", 1)]]
 #    }

class current(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	values = DictField()

class currentdirection(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	values = DictField()

class current_visualisation(Document):
	zid = StringField(db_field='zid', max_length=50, required=True)
	loc =  PointField(db_field='l', required=True)
	date = DateTimeField(db_field='dt', required=True)
	speed = FloatField(db_field='s', required=True)
	direction = FloatField(db_field='d', required=True)

class tide(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	values = DictField()

class tide_visualisation(Document):
	zid = StringField(db_field='zid', max_length=50, required=True)
	polygon = PolygonField(db_field='pl', required=True)
	date = DateTimeField(db_field='dt', required=True)
	depth = FloatField(db_field='d', required=True)
	# meta = {
 #        'indexes': [[("pl", "2dsphere"), ("zid", 1), ("dt", 1)]]
 #    }

class wind(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	values = DictField()

class bathymetry(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	depth = FloatField(db_field='d', required=True)
	zid = StringField(db_field='zid', max_length=50, required=True)

class bathymetry_visualisation(Document):
	zid = StringField(db_field='zid', max_length=50, required=True)
	polygon = PolygonField(db_field='pl', required=True)
	depth = FloatField(db_field='d', required=True)
	# meta = {
 #        'indexes': [[("pl", "2dsphere"), ("zid", 1), ("dt", 1)]]
 #    }

class shoreline(Document):
	lid = StringField(db_field='uzid', max_length=50, required=True)
	line = LineStringField(db_field='ln', auto_index=True, required=True)
	name = StringField(db_field='name', max_length=100, required=True)
	date = DateTimeField(db_field='dt', default=datetime.now)
	created_at = DateTimeField(db_field='ct', default=datetime.now)

class userbathymetry(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	depth = FloatField(db_field='d', required=True)
	email = StringField(db_field='e', max_length=200, required=True)
	uzid = StringField(db_field='uzid', max_length=50, required=True)

class usershoreline(Document):
	lid = StringField(db_field='uzid', max_length=50, required=True)
	line = LineStringField(db_field='ln', auto_index=True, required=True)
	name = StringField(db_field='name', max_length=100, required=True)
	email = StringField(db_field='e', max_length=200, required=True)
	date = DateTimeField(db_field='dt', default=datetime.now)
	created_at = DateTimeField(db_field='ct', default=datetime.now)

class sediment(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	zid = StringField(db_field='zid', max_length=50, required=True)
	month = StringField(db_field='m', required=True)
	angle = FloatField(db_field='a', required=True)
	value = FloatField(db_field='v', required=True)
	meta = {
        'indexes': [[("zid", 1), ("month", 1)]]
    }

