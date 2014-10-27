import sys
import numpy as np
import cv2 as cv

# This class is used for interpolating points
class PointsInterpolator:	
	def __init__(self):
		print "Constructor for class PointsInterpolator"
		return
	
	"""
	Interpolate the given data from the interface
	* Input format: 
	{ 
		'Group i': {
			'direction': 'North',
			'points': [(x1, y1, z1), (x2, y2, z2)]
		}
	}
	* Output format:
	{
		(x1, y1, z1): (r1, g1, b1),
		(x2, y2, z2): (r2, g2, b2)
	}
	"""	
	def interpolate(self, data):
		self._adjustPoints(data)
		self._interpolatePoints(data)
		colouredData = self._fillColor(data)
		return colouredData

	# Adjust data so that each group points is on the same plane
	def _adjustPoints(self, data):
		for key, group in data.iteritems():
			self._adjustGroup(group)
		return

	# Adjust points in a group to be on the same plane
	def _adjustGroup(self, group):
		pts = group['points']
		if(len(pts) < 3):
			print "This set of points does not need adjustment"

		a, b, c, d = self._getPlaneFormula(pts[0], pts[1], pts[2])
		for i in xrange(3, len(pts)):
			x, y, z = pts[i]
			if(c != 0):
				z = (d - a * x - b * y) / c
			pts[i] = (x, y, z)
		group['planeFormula'] = (a, b, c, d)
		return 

	# Get the formula of the plane from 3 given points
	def _getPlaneFormula(self, pt1, pt2, pt3):
		x1, y1, z1 = pt1
		x2, y2, z2 = pt2 
		x3, y3, z3 = pt3
		vector1 = [x3 - x1, y3 - y1, z3 - z1]
		vector2 = [x2 - x1, y2 - y1, z2 - z1]
		a, b, c = np.cross(vector1, vector2)
		d = a * x1 + b * y1 + c * z1
		print a, b, c, d
		return (a, b, c, d)

	# Interpolate points inside each group from the data
	def _interpolatePoints(self, data):
		for key, group in data.iteritems():
			self._interpolateGroup(group)
		return

	# Interpolation points inside the polygon create by the corners in each group
	def _interpolateGroup(self, group):
		pts = group['points']
		if(len(pts) < 3):
			print "This set of points does not have enough points for interpolation"	
		corners = []
		maxX = maxY = maxZ = 0
		minX = minY = minZ = sys.maxint
		for (x, y, z) in pts:
			corners.append((x, y))
			if(x < minX):
				minX = x
			elif (x > maxX):
				maxX = x
			if(y < minY):
				minY = y
			elif(y > maxY):
				maxY = y
			if(z < minZ):
				minZ = z
			elif(z > maxZ):
				maxZ = z
		interpolatedPoints = []
		a, b, c, d = group['planeFormula']
		for x in self._drange(minX, maxX + 1, 1.0):
			for y in self._drange(minY, maxY + 1, 1.0):
				if(not self._pointInPolygon((x,y), corners)):
					continue
				if(c != 0):
					point = (x, y, (d - a * x - b * y) / c)
					interpolatedPoints.append((x, y, (d - a * x - b * y) / c))
				else:
					for z in self._drange(minZ, maxZ + 1, 1.0):
						interpolatedPoints.append((x, y, z))
		group['points'] = interpolatedPoints
		return	

	def _drange(self, x, y, jump):
		while x < y:
			yield x
			x += jump

	def _pointInPolygon(self, point, corners):
		polySides = len(corners)
		i = 0
		j = polySides - 1
		oddNodes= False
		while(i < polySides):
			if((corners[i][1] < point[1] and corners[j][1] >= point[1] 
				or corners[j][1] < point[1] and corners[i][1] >= point[1])
				and (corners[i][0] <= point[0] or corners[j][0] <= point[0])):
				oddNodes = oddNodes ^ (corners[i][0] + (point[1] - corners[i][1]) / (corners[j][1] - corners[i][1]) * (corners[j][0] - corners[i][0]) < point[0])
			j = i
			i += 1

		return oddNodes

	# Fill the color for every point in each group from the data
	def _fillColor(self, data):
		colorData = {}
		for key, group in data.iteritems():
			pts = group['points']
			for point in pts:
				colorData[point] = (255, 0, 0)

		return colorData
