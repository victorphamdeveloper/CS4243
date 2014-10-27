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
	def interpolate(data):
		print "Interpolate points"
		self._adjustPoints(data)
		self._interpolatePoints(data)
		colouredData = self._fillColor(data)
		return colouredData

	# Adjust data so that each group points is on the same plane
	def _adjustPoints(self, data):
		print "Adjust points"
		for key, group in data.iteritems():
			self._adjustGroup(group)
		return

	# Adjust points in a group to be on the same plane
	def _adjustGroup(self, group):
		print "Adjust group"
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
		return (a, b, c, d)

	# Interpolate points inside each group from the data
	def _interpolatePoints(self, data):
		print "Interpolate Points"
		for key, group in data.itermitems():
			self._interpolateGroup(group)
		return

	# Interpolation points inside the polygon create by the corners in each group
	def _interpolateGroup(self, group):
		print "Interpolate group"
		pts = group['points']
		if(len(pts) < 3):
			print "This set of points does not have enough points for interpolation"	
		contour = []
		minX = maxX = minY = maxY = minZ = maxZ = 0.0 
		for (x, y, z) in pts:
			contour.append((x, y))
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
		for x in self.drange(minX, maxX + 1, 1.0):
			for y in self.drange(minY, maxY + 1, 1.0):
				if(cv.pointPolygonTest(contour, (x,y), False)):
					continue
				if(c == 0):
					point = (x, y, (d - a * x - b * y) / c)
					interpolatedPoints.append((x, y, (d - a * x - b * y) / c))
				else:
					for z in self.drange(minZ, maxZ + 1, 1.0):
						interpolatedPoints.append((x, y, z))
		group['points'] = interpolatedPoints
		return	

	def drange(x, y, jump):
		while x < y:
			yield x
			x += jump

	# Fill the color for every point in each group from the data
	def _fillColor(self, data):
		colorData = {}
		for key, group in data.iteritems():
			pts = group['pts']
			for point in pts:
				colorData[point] = (255, 0, 0)

		return colorData
