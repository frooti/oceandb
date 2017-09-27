# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from mongoengine import *
from datetime import datetime

connect('ocean')

class order(Document):
	oid = StringField(db_field='oid', max_length=50, required=True)
	email = StringField(db_field='e', max_length=200, required=True)
	organization = StringField(db_field='o', max_length=200, required=True)
	polygon = PolygonField(db_field='p', auto_index=True, required=True)
	data = StringField(db_field='d', max_length=50, required=True)
	price = DecimalField(db_field='p', precision=2, rounding='ROUND_HALF_UP', required=True) 
	payment_status = BooleanField(db_field='ps', default=False)
	download_link = StringField(db_field='dl', default=None)
	email_sent = BooleanField(db_field='em', default=False)
	created_at = DateTimeField(db_field='ct', default=datetime.now())
	processed_at = DateTimeField(db_field='pt', default=None)

class wave(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	height = FloatField(db_field='h', required=True)

class bathymetry(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	depth = FloatField(db_field='d', required=True)
