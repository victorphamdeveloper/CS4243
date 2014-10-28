import copy
import json

from pointsInterpolator import *
from perspectiveProjector import *

import cv2
import cv2.cv as cv
import numpy as np

#This class is used for generating test data instead of
#having to create data through the interface repeatedly
class DataGenerator:
	IMAGE_ORIGINAL_WIDTH = 1632.0
	IMAGE_ORIGINAL_HEIGHT = 1224.0

	def __init__(self):
		with open('data.json', 'rb') as fp:
			groupsData = json.load(fp)
		#groupsData.pop('Group 4', None)
		#groupsData.pop('Group 2', None)
		#roupsData.pop('Group 3', None)
		#groupsData.pop('Group 5', None)
		pointsInterpolator = PointsInterpolator()
		interpolatedData = pointsInterpolator.interpolate(groupsData)
		perspectiveProjector = PerspectiveProjector()
		cameraPosition = [self.IMAGE_ORIGINAL_WIDTH, self.IMAGE_ORIGINAL_HEIGHT / 1.5, 0]
		orientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
		results = perspectiveProjector.performPerspective(copy.deepcopy(interpolatedData), cameraPosition, orientation)
		#results = persectiveProjector.performPerspectiveWithYRotatedAngle(copy.deepcopy(interpolatedData), cameraPosition, np.pi/6.0)
		imageFrame = np.zeros((int(self.IMAGE_ORIGINAL_HEIGHT),int(self.IMAGE_ORIGINAL_WIDTH),3), np.uint8)
		for point, color in results.iteritems():
			x = int(point[0] + self.IMAGE_ORIGINAL_WIDTH  / 2.0)
			y = int(point[1] + self.IMAGE_ORIGINAL_HEIGHT / 2.0)
			if(0 <= x and x < self.IMAGE_ORIGINAL_WIDTH and 0 <= y and y < self.IMAGE_ORIGINAL_HEIGHT):
				imageFrame[y][x] = [color[2], color[1], color[0]]

		winname = "imageWin"
		win = cv.NamedWindow(winname, cv.CV_WINDOW_AUTOSIZE)
		cv2.imshow('imageWin', imageFrame)
		cv2.waitKey(10000)
		cv.DestroyWindow(winname)
		return

	def initializeData(self):
		print "Initialize data for testing"
		return

DataGenerator()