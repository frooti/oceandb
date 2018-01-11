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
coordinates = linestring.getElementsByTagName('coordinates').childNodes[0].data
coordinates = coordinates.strip().split(' ')
print coordinates[0]