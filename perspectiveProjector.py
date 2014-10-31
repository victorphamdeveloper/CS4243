import sys
import numpy as np
from numpy import linalg as la
from pointsInterpolator import *

# This class is used for performing perspective projection
class PerspectiveProjector:
	# Constant declaration
	IMG_NAME = "project.jpg"
	FOCAL_LENGTH = 800
	X_PIXEL_SCALING = Y_PIXEL_SCALING = 1
	X_CENTER_OFFSET = Y_CENTER_OFFSET= 0
	Y_ROTATIONAL_AXIS = np.array([0, 1, 0])

	def __init__(self):
		return

	"""
	Perform perspective with given camera position and its rotation
	on a set of points with given colours
	* Input Format:
	{
		(x1, y1, z1): (r1, g1, b1),
		(x2, y2, z2): (r2, g2, b2)
	}
	* Output Format:
		2D array represent every pixel in the frame
	"""

	def performPerspectiveWithYRotatedAngle(self, data, initialCameraPosition, angle):
		cameraRotationalAxes = self._quat2rot(self._getQuaternion(self.Y_ROTATIONAL_AXIS, angle))
		cameraPos = self._translateCameraWithAngle(initialCameraPosition, self.Y_ROTATIONAL_AXIS, -angle)
		return self.performPerspective(data, cameraPos, cameraRotationalAxes)

	def performPerspective(self, data, cameraPosition, orientation):
		result  = {}
		zBuffer = {}
		print "Start Performing Perspective Projection..."
		for groupKey, group in data.iteritems():
			pointDict = group['colors']
			tempColor = {}
			tempCount = {}
			tempDist = {}
			projectedCorners = []
			minValues = [sys.maxint, sys.maxint]
			maxValues = [0, 0]
			for corner in group['corners']:
				corner = np.asarray(corner)
				den = np.dot(corner - cameraPosition, np.asarray(orientation)[2])
				if(den != 0):
					projectedX = self.FOCAL_LENGTH * np.dot(corner - cameraPosition, np.asarray(orientation)[0]) * self.X_PIXEL_SCALING / den + self.X_CENTER_OFFSET
					projectedY = self.FOCAL_LENGTH * np.dot(corner - cameraPosition, np.asarray(orientation)[1]) * self.Y_PIXEL_SCALING / den + self.Y_CENTER_OFFSET
					projectedCorner = (int(projectedX), int(projectedY))
					projectedCorners.append(projectedCorner)

			for pointKey, color in pointDict.iteritems():
				point = np.asarray(pointKey)
				den = np.dot(point - cameraPosition, np.asarray(orientation)[2])
				if (den != 0):
					projectedX = self.FOCAL_LENGTH * np.dot(point - cameraPosition, np.asarray(orientation)[0]) * self.X_PIXEL_SCALING / den + self.X_CENTER_OFFSET
					projectedY = self.FOCAL_LENGTH * np.dot(point - cameraPosition, np.asarray(orientation)[1]) * self.Y_PIXEL_SCALING / den + self.Y_CENTER_OFFSET
					projectedPoint = (int(projectedX), int(projectedY))
					distance = la.norm(cameraPosition - point)
					if(not projectedPoint in tempCount):
						tempCount[projectedPoint] = 1
						tempColor[projectedPoint] = color.astype(dtype='int64')
					else:
						tempCount[projectedPoint] += 1
						accumulatedColor = tempColor[projectedPoint]
						tempColor[projectedPoint] = (accumulatedColor[0] + color[0],
													accumulatedColor[1] + color[1],
													accumulatedColor[2] + color[2])
					tempDist[projectedPoint] = distance

			for projectedCorner in projectedCorners:
				for i in range(2):
					if(projectedCorner[i] < minValues[i]):
						minValues[i] = projectedCorner[i]
					if(projectedCorner[i] > maxValues[i]):
						maxValues[i] = projectedCorner[i]

			for x in xrange(minValues[0], maxValues[0] + 1, 1):
				for y in xrange(minValues[1], maxValues[1] + 1, 1):
					if((not (x, y) in tempColor) and PointsInterpolator.pointInPolygon(x, y, projectedCorners)):
						for i in xrange(1, 11):
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

	# Function to translate the camera
	def _translateCameraWithAngle(self, cameraPos, rotationalAxis, angle):
		q = self._getQuaternion(rotationalAxis, angle)
		negate_q = np.array([q[0], -q[1], -q[2], -q[3]])
		cameraQuaternion = np.array([0, cameraPos[0], cameraPos[1], cameraPos[2]])
		result = self._qualtmult(self._qualtmult(q, cameraQuaternion), negate_q)
		return np.array([result[1], result[2], result[3]])

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
