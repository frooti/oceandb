import sys
import os
from os import listdir
from os.path import isfile, join
sys.path.append('/home/dataraft/projects/oceandb')
sys.stdout.flush()

from cStringIO import StringIO
from xml.dom.minidom import parseString
from zipfile import ZipFile
import math
import geojson

import json
from datetime import datetime
from download.models import shoreline
import uuid

## CONFIG ##
filename = '/tmp/test.kmz'
## CONFIG ##

def openKMZ(filename):
    zip=ZipFile(filename)
    for z in zip.filelist:
        if z.filename[-4:] == '.kml':
            fstring=zip.read(z)
            break
    else:
        raise Exception("Could not find kml file in %s" % filename)
    return fstring

def openKML(filename):
    try:
        fstring=openKMZ(filename)
    except Exception:
        fstring=open(filename,'r').read()
    return parseString(fstring)

xml = openKML(filename)
linestring = xml.getElementsByTagName('LineString')[0]
coordinates = linestring.getElementsByTagName('coordinates')[0].childNodes[0].data
coordinates = coordinates.strip().split(' ')
points = []

for p in coordinates:
    p = p.strip(',')
    points.append((round(float(p[0]), 5), round(float(p[1]), 5)))
print len(points)

name = ''
date = xml.getElementsByTagName('Placemark')[0].getElementsByTagName('name')[0].childNodes[0].data
date = datetime.strptime(date, "%d/%m/%Y")

s = shoreline(lid=str(uuid.uuid4()))
s.line = json.loads(geojson.dumps(points))
s.name = name
s.date = date
s.save()
print s.lid
print 'completed!'