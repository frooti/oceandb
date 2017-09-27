# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from mongoengine import *

connect('ocean')

class wave(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	height = FloatField(db_field='h', required=True)

class bathymetry(Document):
	loc = PointField(db_field='l', auto_index=True, required=True)
	depth = FloatField(db_field='d', required=True)
