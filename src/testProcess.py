# System Dependence
import copy
import time

# External Dependence
import cv2
import cv2.cv as cv
import numpy as np

# Class Dependence
from pointsInterpolator import *
from perspectiveProjector import *
from dataGenerator import *

###########################################################
#                   Testing Script                        #
###########################################################

current_milli_time = lambda: int(round(time.time() * 1000))

IMAGE_ORIGINAL_WIDTH = 800
IMAGE_ORIGINAL_HEIGHT = 600

# Retrieve data
dataGenerator = DataGenerator()
groupsData = dataGenerator.loadDataFromFile("data/allData.json")

# Interpolate data
start = current_milli_time()
pointsInterpolator = PointsInterpolator()
interpolatedData = pointsInterpolator.interpolate(groupsData)
print 'Time taken for interpolation: ', (current_milli_time() - start), 'ms'

# Perspective Projection
start = current_milli_time()
perspectiveProjector = PerspectiveProjector()
cameraPosition = [IMAGE_ORIGINAL_WIDTH / 2.0, IMAGE_ORIGINAL_HEIGHT * 2 / 3.0, -5]
orientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
perspectiveProjector.testAlignmentByUsingDefaultColor(interpolatedData)

#results = perspectiveProjector.performPerspectiveWithYRotatedAngle(copy.deepcopy(interpolatedData), cameraPosition, np.pi / 3.0)
results = perspectiveProjector.performPerspective(copy.deepcopy(interpolatedData), cameraPosition, orientation )
print 'Time taken for perspective projection: ', (current_milli_time() - start), 'ms'
imageFrame = np.zeros((int(IMAGE_ORIGINAL_HEIGHT),int(IMAGE_ORIGINAL_WIDTH),3), np.uint8)
for point, color in results.iteritems():
	x = int(point[0] + IMAGE_ORIGINAL_WIDTH  / 2.0)
	y = int(point[1] + IMAGE_ORIGINAL_HEIGHT / 2.0)
	if(0 <= x and x < IMAGE_ORIGINAL_WIDTH and 0 <= y and y < IMAGE_ORIGINAL_HEIGHT):
		imageFrame[y][x] = [color[0], color[1], color[2]]

winname = "imageWin"
win = cv.NamedWindow(winname, cv.CV_WINDOW_AUTOSIZE)
imageFrame = cv2.resize(imageFrame, (800, 600))
cv2.imshow('imageWin', imageFrame)
cv2.waitKey(0)
cv.DestroyWindow(winname)