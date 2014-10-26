import sys

# This class is used for performing perspective projection
class PerspectiveProjector:
	# Constant declaration
	IMG_NAME = "project.jpg"
	FOCAL_LENGTH = 1
	X_PIXEL_SCALING = Y_PIXEL_SCALING = 1 
	X_CENTER_OFFSET = Y_CENTER_OFFSET= 0
	
	def __init__(self):
		print "Constructor for class PerspectiveProjector"
		return

	# Test function
	def processData(self, data):
		print "Start processing data for video generation"
		print data
		
		colorData = self.readColor(data)
		pointDict = {}
		for group, groupData in colorData.iteritems():
			pointDict = dict(pointDict.items() + groupData["points"].items()) 
		
		cameraPosition = [0, 0, 0]
		orientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
		filteredPoints = self._filterAlignedPoints(pointDict, cameraPosition)
		projectedPoints = self.performPerspective(filteredPoints, cameraPosition, orientation)
		print projectedPoints
		
		return
	
	# Test function
	def readColor(self, data):
		image = cv.imread(self.IMG_NAME, cv.CV_LOAD_IMAGE_COLOR)
		colorMappedData = copy.deepcopy(data)
		
		for group, groupData in data.iteritems():
			colorMappedData[group]["points"] = {}
			for pointData in groupData["points"]:
				colorMappedData[group]["points"][pointData] = image[pointData[0]][pointData[1]]
			
		return colorMappedData

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
	def performPerspective(self, pointDict, cameraPosition, orientation):
		result = {}
		for key, color in pointDict.iteritems():
			point = np.asarray(key) 
			den = np.dot(point - cameraPosition, np.asarray(orientation)[2])
			if (den != 0):
				projectedX = self.FOCAL_LENGTH * np.dot(point - cameraPosition, np.asarray(orientation)[0]) * self.X_PIXEL_SCALING / den + self.X_CENTER_OFFSET
				projectedY = self.FOCAL_LENGTH * np.dot(point - cameraPosition, np.asarray(orientation)[1]) * self.Y_PIXEL_SCALING / den + self.Y_CENTER_OFFSET
				projectedPoint = (projectedX, projectedY)
			
				result[projectedPoint] = color
			
		return result
	
	def _filterAlignedPoints(self, pointDict, cameraPosition):
		filteredPointDict = pointDict
		keys = pointDict.keys()
		length = len(keys)
		points = [0, 0, 0] * length
		deletedKeys = set()
		
		for i in range(length):
			points[i] = np.array(keys[i])
			
		for i in range(length):
			for j in xrange(i + 1, length - 1):
				if (keys[i] not in deletedKeys) and (keys[j] not in deletedKeys) and (self._isAligned(cameraPosition, points[i], points[j])):
					if (la.norm(cameraPosition - points[i]) > la.norm(cameraPosition - points[j])):
						del pointDict[keys[i]]
						deletedKeys.add(keys[i])
					else:
						del pointDict[keys[j]]
						deletedKeys.add(keys[j])  
					
		return filteredPointDict
	
	def _isAligned(self, point1, point2, point3):
		vector12 = point2 - point1
		vector13 = point3 - point1
		crossProduct = np.cross(vector12, vector13)
		isPointsAligned = (np.count_nonzero(crossProduct) == 0)
		
		return isPointsAligned	
