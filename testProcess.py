from pointsInterpolator import *
from perspectiveProjector import *
from dataGenerator import *

import copy
import cv2 
import cv2.cv as cv

IMAGE_ORIGINAL_WIDTH = 1632.0
IMAGE_ORIGINAL_HEIGHT = 1224.0

dataGenerator = DataGenerator()
groupsData = dataGenerator.loadDataFromFile("allData.json")

pointsInterpolator = PointsInterpolator()
interpolatedData = pointsInterpolator.interpolate(groupsData)

perspectiveProjector = PerspectiveProjector()
cameraPosition = [IMAGE_ORIGINAL_WIDTH / 2.0, IMAGE_ORIGINAL_HEIGHT * 2 / 3.0, -5]
orientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
results = perspectiveProjector.performPerspective(copy.deepcopy(interpolatedData), cameraPosition, orientation )

imageFrame = np.zeros((int(IMAGE_ORIGINAL_HEIGHT),int(IMAGE_ORIGINAL_WIDTH),3), np.uint8)
for point, color in results.iteritems():
	x = int(point[0] + IMAGE_ORIGINAL_WIDTH  / 2.0)
	y = int(point[1] + IMAGE_ORIGINAL_HEIGHT / 2.0)
	if(0 <= x and x < IMAGE_ORIGINAL_WIDTH and 0 <= y and y < IMAGE_ORIGINAL_HEIGHT):
		imageFrame[y][x] = [color[2], color[1], color[0]]

winname = "imageWin"
win = cv.NamedWindow(winname, cv.CV_WINDOW_AUTOSIZE)
imageFrame = cv2.resize(imageFrame, (1200, 900))
cv2.imshow('imageWin', imageFrame)
cv2.waitKey(0)
cv.DestroyWindow(winname)