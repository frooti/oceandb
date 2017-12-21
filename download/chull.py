from scipy.spatial import ConvexHull
import csv

file_path = '/Users/ravi/Desktop/bathy_zones/cochin_port/thottapalli.xyz'

points = []
chull  = []

with open(file_path, 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
	for i, row in enumerate(spamreader):
		if i==0:
			continue
		elif row:
			points.append([float(row[1]), float(row[0])])

	hull = ConvexHull(points)

	for i in hull.vertices:
		chull.append(points[i])

	chull = chull+[chull[0]]
	print chull
