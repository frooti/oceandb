import csv
import json

points = []
polygon = {'type':'Polygon', 'coordinates':[points]}

with open('/Users/ravi/Downloads/coords/Bathy_LatLong_Part_8_coords.csv') as f:
	reader = csv.reader(f)
	c = 0
	for row in reader:
		c=c+1
		if c==1:
			continue		
		points.append([float(row[1]), float(row[2])])
	print polygon
