import sys
import numpy as np
import cv2 as cv

# This class is used for interpolating points
class PointsInterpolator:	
	def __init__(self):
		print "Constructor for class PointsInterpolator"
		return
	
	# Basic implementation	
	def interpolate(data):
		print "Interpolate points"
		self.adjustPoints(data)
		interpolatedData = self.interpolatePoints(data)
		colouredData = self.fillColor(interpolatedData)
		return colouredData

	def adjustPoints(self, data):
		print "Adjust points"
		for key, group in data.iteritems():
			self.adjustGroup(group)
		return

	def adjustGroup(self, group):
		print "Adjust group"
		pts = group['points']
		if(len(pts) < 3):
			print "This set of points does not need adjustment"

		a, b, c, d = self.getPlaneFormula(pts[0], pts[1], pts[2])
		for i in xrange(3, len(pts)):
			x, y, z = pts[i]
			if(c != 0):
				z = (d - a * x - b * y) / c
			pts[i] = (x, y, z)
		group['planeFormula'] = (a, b, c, d)
		return 

	def getPlaneFormula(self, pt1, pt2, pt3):
		x1, y1, z1 = pt1
		x2, y2, z2 = pt2 
		x3, y3, z3 = pt3
		vector1 = [x3 - x1, y3 - y1, z3 - z1]
		vector2 = [x2 - x1, y2 - y1, z2 - z1]
		a, b, c = np.cross(vector1, vector2)
		d = a * x1 + b * y1 + c * z1
		return (a, b, c, d)


	def interpolatePoints(self, data):
		print "Interpolate Points"
		for key, group in data.itermitems():
			self.interpolateGroup(group)
		return

	def interpolateGroup(self, group):
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
		for x in xrange(minX, maxX + 1):
			for y in xrange(minY, maxY + 1):
				if(cv.pointPolygonTest(contour, (x,y), False)):
					continue
				if(c == 0):
					point = (x, y, (d - a * x - b * y) / c)
					interpolatedPoints.append((x, y, (d - a * x - b * y) / c))
				else:
					for z in xrange(minZ, maxZ + 1):
						interpolatedPoints.append((x, y, z))
		group['points'] = interpolatedPoints
		return

	# Need to implement
	def fillColor(self, data):
		print "Fill Colors"
		return
