import sys
import numpy as np
import cv2 as cv

# This class is used for interpolating points
class PointsInterpolator:
	def __init__(self):
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
		print "Start Performing Interpolation..."
		self._adjustPoints(data)
		self._interpolatePoints(data)
		colouredData = self._fillColor(data)
		print "Finish Performing Interpolation :)"
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
		maxValues = [0.0,  0.0,  0.0]
		minValues = [sys.maxint, sys.maxint, sys.maxint]
		for point in pts:
			for i in range(3):
				if(point[i] < minValues[i]):
					minValues[i] = point[i]
				if(point[i] > maxValues[i]):
					maxValues[i] = point[i]
		disRank = [maxValues[0] - minValues[0], maxValues[1] - minValues[1], maxValues[2] - minValues[2]]
		disRank.sort()
		maxAxis = secondMaxAxis = thirdMaxAxis = -1
		for i in range(3):
			if(maxAxis == -1 and maxValues[i] - minValues[i] == disRank[2]):
				maxAxis = i
			elif(secondMaxAxis == -1 and maxValues[i] - minValues[i] == disRank[1]):
				secondMaxAxis = i
			else:
				thirdMaxAxis = i
		for point in pts:
			if(not (point[secondMaxAxis], point[maxAxis]) in corners):
				corners.append((point[secondMaxAxis], point[maxAxis]))

		interpolatedPoints = []
		planeFormula = group['planeFormula']
		for m in self._drange(minValues[maxAxis], maxValues[maxAxis] + 1, 1.0):
			for n in self._drange(minValues[secondMaxAxis], maxValues[secondMaxAxis] + 1, 1.0):
				if(not self._pointInPolygon((n,m), corners)):
					continue
				point = [0, 0, 0]
				point[maxAxis] = m
				point[secondMaxAxis] = n
				point[thirdMaxAxis] = (planeFormula[3] - planeFormula[maxAxis] * m - planeFormula[secondMaxAxis] * n ) / planeFormula[thirdMaxAxis]
				interpolatedPoints.append(tuple(point))
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
				if(key == 'Group 1'):
					colorData[point] = (255, 0, 0)
				elif(key == 'Group 2'):
					colorData[point] = (0, 255, 0)
				elif(key == 'Group 3'):
					colorData[point] = (0, 0, 255)
				elif(key == 'Group 4'):
					colorData[point] = (255, 255, 255)
				else:
					colorData[point] = (189, 190, 0)

		return colorData
