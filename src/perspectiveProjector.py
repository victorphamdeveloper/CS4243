# System Dependence
import sys
import random

# External Dependence
import numpy as np
from numpy import linalg as la
import cv2
import cv2.cv as cv

# Class Dependence
from pointsInterpolator import *

###########################################################
#                   Perspective Projector                 #
###########################################################
class PerspectiveProjector:
	# Constant declaration
	IMG_NAME = "project.jpg"
	X_PIXEL_SCALING = Y_PIXEL_SCALING = 1
	X_CENTER_OFFSET = Y_CENTER_OFFSET= 0
	Y_ROTATIONAL_AXIS = np.array([0, 1, 0])
	IMAGE_ORIGINAL_WIDTH = 800
	IMAGE_ORIGINAL_HEIGHT = 600

	def __init__(self, isTestingLayout):
		self.FOCAL_LENGTH = 800.0 # default focal length
		self.isTestingLayout = isTestingLayout
		return

	# Fill the color for every point in each group from the data
	def fillColor(self, data, initialCameraPosition, orientation):
		print "Start filling color..."
		imageSize = (self.IMAGE_ORIGINAL_WIDTH, self.IMAGE_ORIGINAL_HEIGHT)
		xOrientation = np.asarray(orientation)[0]
		yOrientation = np.asarray(orientation)[1]
		zOrientation = np.asarray(orientation)[2]

		image = cv2.imread("images/project.jpg", cv2.CV_LOAD_IMAGE_COLOR)
		image = cv2.resize(image, imageSize)
		width = image.shape[1]
		height = image.shape[0]
		dstGroupMap = {}
		isSideWallGroupMap = {}
		isFlatRoofGroupMap = {}
		isBoundaryWallGroupMap = {}
		isTentedRoofGroupMap = {}
		for groupKey, group in data.iteritems():
			group['colors'] = {}
			# Projection
			projectedCorners = []
			groupPoints = group['corners'] + group['points'] 
			srcGroupMap = {}
			for i in range(len(groupPoints)):
				point = groupPoints[i]
				pointArr = np.asarray(point)
				den = np.dot(pointArr - initialCameraPosition, zOrientation)
				if (den != 0):
					projectedX = (self.FOCAL_LENGTH * np.dot(pointArr - initialCameraPosition, xOrientation) 
								* self.X_PIXEL_SCALING / den 
								+ self.X_CENTER_OFFSET 
								+ self.IMAGE_ORIGINAL_WIDTH / 2.0)
					projectedY = (self.FOCAL_LENGTH 
								* np.dot(pointArr - initialCameraPosition, yOrientation) 
								* self.Y_PIXEL_SCALING / den 
								+ self.Y_CENTER_OFFSET 
								+ self.IMAGE_ORIGINAL_HEIGHT / 2.0)
					projectedPoint = (int(projectedX), int(projectedY))
					if(i < len(group['corners'])):
						projectedCorners.append(projectedPoint)
					if(not projectedPoint in srcGroupMap):
						srcGroupMap[projectedPoint] = [pointArr]
					else:
						srcGroupMap[projectedPoint].append(pointArr)

			# Filter hidden surface
			src = self.verticalReshape(projectedCorners)
			dst = self.verticalReshape(group['2Dpoints'])
			transformationMatrix, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
			finalSrc = srcGroupMap.keys()
			finalDst = np.int32(cv2.perspectiveTransform(
																									self.verticalReshape(finalSrc), 
																									transformationMatrix))

			# Check for hidden groups
			isBoundaryWall = self.isOutOfFrame(group['2Dpoints'][0]) or self.isOutOfFrame(group['2Dpoints'][1]) or self.isOutOfFrame(group['2Dpoints'][2]) or self.isOutOfFrame(group['2Dpoints'][3])
			if isBoundaryWall:
				isBoundaryWallGroupMap[groupKey] = True

			xSet = set([group['2Dpoints'][0][0],group['2Dpoints'][1][0],group['2Dpoints'][2][0],group['2Dpoints'][3][0]])
			ySet = set([group['2Dpoints'][0][1],group['2Dpoints'][1][1],group['2Dpoints'][2][1],group['2Dpoints'][3][1]])

			isTentedRoof = (len(xSet) == len(ySet) == 2)
			if isTentedRoof:
				isTentedRoofGroupMap[groupKey] = True
				continue

			isSideWall = (group['2Dpoints'][0][0] == group['2Dpoints'][1][0] == group['2Dpoints'][2][0] == group['2Dpoints'][3][0])
			if isSideWall :
				isSideWallGroupMap[groupKey] = True
				continue

			isFlatRoof = (group['corners'][0][1] == group['corners'][1][1] == group['corners'][2][1] == group['corners'][3][1]) 
			if isFlatRoof :
				isFlatRoofGroupMap[groupKey] = True
				continue

			tempGroupMap = {}
			for i in range(len(finalDst)):
				dstCoord = tuple(finalDst[i].ravel())
				if(dstCoord[0] < 0 or dstCoord[0] >= self.IMAGE_ORIGINAL_WIDTH 
													 or dstCoord[1] < 0 
													 or dstCoord[1] >= self.IMAGE_ORIGINAL_HEIGHT):
					continue
				srcCoord = finalSrc[i]
				if(not dstCoord in tempGroupMap):
					tempGroupMap[dstCoord] = {'group': groupKey, 'dist': sys.maxint, 'points': []}
				for point in srcGroupMap[srcCoord]:
					distance = la.norm(initialCameraPosition - point)
					if(distance < tempGroupMap[dstCoord]['dist']):
						tempGroupMap[dstCoord]['dist'] = distance
					tempGroupMap[dstCoord]['points'].append(point)
			for coord, group in tempGroupMap.iteritems():
				if(not coord in dstGroupMap):
					dstGroupMap[coord] = group
				else:
					if(dstGroupMap[coord]['dist'] > group['dist']):		
						dstGroupMap[coord] = group

		# Assign front colors
		for coord, group in dstGroupMap.iteritems():
			groupKey = group['group']
			for point in group['points']:
				data[groupKey]['colors'][point] = image[round(coord[1])][round(coord[0])]	
		
		# Assign colors for remaining hidden points
		for groupKey, group in data.iteritems():
			# Side wall or Flat roof
			if(groupKey in isSideWallGroupMap or groupKey in isFlatRoofGroupMap):
				for point in group['points']:
					group['colors'][point] = image[400][400]
			elif (groupKey in isBoundaryWallGroupMap): # Other Hidden Surfaces to be implemented
				for point in group['points']:
					if not point in group['colors']:
						group['colors'][point] = image[400][400]
			elif (groupKey in isTentedRoofGroupMap):
				for point in group['points']:
					group['colors'][point] = image[575, 353]
					print group['colors'][point]
			else:
				for point in group['points']:
					if not point in group['colors']:
						group['colors'][point] = image[400][400]


		for key, group in data.iteritems():
			group['points'] = None

		print "Finish filling color"
		return

	def isOutOfFrame(self, point):
		return (point[0] < 0 or point[0] >= self.IMAGE_ORIGINAL_WIDTH or point[1] < 0 or point[1] >= self.IMAGE_ORIGINAL_HEIGHT)

	def verticalReshape(self, arr):
		return np.float32(arr).reshape(-1, 1, 2)

	def testAlignmentByUsingDefaultColor(self, data):
		for key, group in data.iteritems():
			colorData = {}
			pts = group['points']
			randomRed = random.randint(0, 255)
			randomGreen = random.randint(0, 255)
			randomBlue = random.randint(0, 255)
			for point in pts:
				colorData[point] = np.array([randomRed, randomGreen, randomBlue])
			group['colors'] = colorData
			group['points'] = None
		return

	"""
	Perform perspective with given camera position and its rotation
	on a set of points with given colours
	* Input Format:
	{
		'Group i': {
			'direction': 'North',
			'points':{
				[(x1, y1, z1), ...]			`
			}	
			'corners':{
				[(x1, y1, z1), (x2, y2, z2), (x3, y3, z3)]
			},
			'2Dpoints':{
				[(x1, y1), (x2, y2), (x3, y3)]
			}
		}
	}
	* Output Format:
		2D array represent every pixel in the frame
	"""
	def performPerspective(self, data, cameraPosition, orientation):
		result  = {}
		zBuffer = {}
		print "Start Performing Perspective Projection..."
		for groupKey, group in data.iteritems():
			pointDict = group['colors']
			tempColor = {}
			tempCount = {}
			tempDist = {}
			minValues = [sys.maxint, sys.maxint]
			maxValues = [0, 0]
			
			for pointKey, color in pointDict.iteritems():
				point = np.asarray(pointKey)
				den = np.dot(point - cameraPosition, np.asarray(orientation)[2])
				if (den > 0):
					projectedX = (self.FOCAL_LENGTH 
												* np.dot(point - cameraPosition, np.asarray(orientation)[0]) 
												* self.X_PIXEL_SCALING / den 
												+ self.X_CENTER_OFFSET)
					if(projectedX < minValues[0]):
						minValues[0] = projectedX
					if(projectedX > maxValues[0]):
						maxValues[0] = projectedX
					projectedY = (self.FOCAL_LENGTH 
												* np.dot(point - cameraPosition, np.asarray(orientation)[1]) 
												* self.Y_PIXEL_SCALING / den 
												+ self.Y_CENTER_OFFSET)
					if(projectedY < minValues[1]):
						minValues[1] = projectedY
					if(projectedY > maxValues[1]):
						maxValues[1] = projectedY
					projectedPoint = (int(projectedX), int(projectedY))
					distance = la.norm(cameraPosition - point)
					if(not projectedPoint in tempCount):
						tempCount[projectedPoint] = 1
						tempColor[projectedPoint] = color.astype(dtype='int64')
					else:
						tempCount[projectedPoint] += 1
						accumulatedColor = tempColor[projectedPoint]
						tempColor[projectedPoint] = (	accumulatedColor[0] + color[0],
																					accumulatedColor[1] + color[1],
																					accumulatedColor[2] + color[2])
					tempDist[projectedPoint] = distance

			if not self.isTestingLayout:
				for x in xrange(minValues[0], maxValues[0] + 1, 1):
					for y in xrange(minValues[1], maxValues[1] + 1, 1):
						if(not (x, y) in tempColor):
							count = 0
							for i in xrange(1, 7):
								if((x + i, y) in tempColor): count += 1
								if((x - i, y) in tempColor): count += 1
								if((x, y + i) in tempColor): count += 1
								if((x, y - i) in tempColor): count += 1

							if(count > 2):
								for i in xrange(1, 7):
									points = []
									for m in xrange(-i, i + 1, 1):
										for n in xrange(-i, i + 1, 1):
											if(np.abs(m) != i and np.abs(n) != i):
												continue
											point = (x + m, y + n)
											if point in tempColor:
												count = tempCount[point]
												if(count > 1):
													color = tempColor[point]
													tempColor[point] = tuple([round(u / count) for u in color])
													tempCount[point] = 1
												points.append(point)
									if(len(points) != 0):
										counter = [0, 0, 0, 0, 0]
										for point in points:
											counter[0] += tempColor[point][0]
											counter[1] += tempColor[point][1]
											counter[2] += tempColor[point][2]
											counter[3] += tempDist[point]
											counter[4] += tempCount[point]
										tempColor[(x, y)] = (counter[0], counter[1], counter[2])
										tempCount[(x, y)] = counter[4]
										tempDist[(x, y)] = counter[3] / counter[4]
										break 
			
			for point in tempColor:
				color = tempColor[point]
				count = tempCount[point]
				if(not point in result):
					result[point] = tuple([round(x / count) for x in color])
					zBuffer[point] = tempDist[point]
				else:
					if(tempDist[point] < zBuffer[point]):
						result[point] = tuple([round(x / count) for x in color])
						zBuffer[point] = tempDist[point]

		print "Finish Performing Perspective Projection :)"
		return result

	def performPerspectiveWithYRotatedAngle(self, data, initialCameraPosition, angle):
		cameraRotationalAxes = self._quat2rot(self._getQuaternion(self.Y_ROTATIONAL_AXIS, angle))
		return self.performPerspective(data, initialCameraPosition, cameraRotationalAxes)

	##################### SUPPORT FUNCTIONS ##############################
	# Function for multiplying quaternion
	def _qualtmult(self, p, q):
		p0 = p[0]
		p1 = p[1]
		p2 = p[2]
		p3 = p[3]
		q0 = q[0]
		q1 = q[1]
		q2 = q[2]
		q3 = q[3]

		# Start computing
		out = [0, 0, 0, 0] #output array
		out[0] = p0 * q0 - p1 * q1 - p2 * q2 - p3 * q3
		out[1] = p0 * q1 + p1 * q0 + p2 * q3 - p3 * q2
		out[2] = p0 * q2 - p1 * q3 + p2 * q0 + p3 * q1
		out[3] = p0 * q3 + p1 * q2 - p2 * q1 + p3 * q0

		return out

	# Retrieve corresponding quaternion from angle and rotational axis
	def _getQuaternion(self, rotationalAxis, angle):
		cosAngle = np.cos(angle / 2.0)
		sinAngle = np.sin(angle / 2.0)
		return np.array([cosAngle, 0, sinAngle, 0])

	# Function to create rotation matrix from quaternion
	def _quat2rot(self, q) :
		q0 = q[0]
		q1 = q[1]
		q2 = q[2]
		q3 = q[3]

		#Start computing
		out = np.zeros((3, 3))
		out[0][0] = np.power(q0, 2) + np.power(q1, 2) - np.power(q2, 2) - np.power(q3, 2)
		out[0][1] = 2 * (q1 * q2 - q0 * q3)
		out[0][2] = 2 * (q1 * q3 + q0 * q2)
		out[1][0] = 2 * (q1 * q2 + q0 * q3)
		out[1][1] = np.power(q0, 2) + np.power(q2, 2) - np.power(q1, 2) - np.power(q3, 2)
		out[1][2] = 2 * (q2 * q3 - q0 * q1)
		out[2][0] = 2 * (q1 * q3 - q0 * q2)
		out[2][1] = 2 * (q2 * q3 + q0 * q1)
		out[2][2] = np.power(q0, 2) + np.power(q3, 2) - np.power(q1, 2) - np.power(q2, 2)

		return np.matrix(out)