# System Dependence
import sys
import copy
import json
import time

# Class Dependence
from pointsInterpolator import *
from perspectiveProjector import *
from videoGenerator import *
from cameraPathGenerator import *
from dataGenerator import *

# External Dependence
from PyQt4 import QtGui, QtCore
import cv2
import cv2.cv as cv
import numpy as np

###########################################################
#                   Main Executable  		                  #
###########################################################
class CS4243Project(QtGui.QWidget):
	# Constant Declaration
	DIRECTIONS = ["None", "North", "South", "West", "East", "Upwards", "Downwards"]
	IMAGE_ORIGINAL_WIDTH = 800
	IMAGE_ORIGINAL_HEIGHT = 600

	def mousePressEvent(self, event):
		super(CS4243Project, self).mousePressEvent(event)
		heightDist = int((self.screenSize.height() - self.imageSize.height()) / 2.0)
		if(event.y() < self.image.pos().y() 
				or event.y() > self.imageSize.height() + self.image.pos().y()):
			return
		xCoord = event.x()
		yCoord = event.y() - self.image.pos().y()
		inversedYCoord = self.imageSize.height() - yCoord
		if(xCoord > self.imageSize.width()):
			return
		currentGroup = self.groups[str(self.groupComboBox.currentText())]
		currentGroup['points'].appendRow(
										[QtGui.QStandardItem(QtCore.QString(str(xCoord))),
										 QtGui.QStandardItem(QtCore.QString(str(inversedYCoord))),
										 QtGui.QStandardItem(QtCore.QString(str(0))),
										 QtGui.QStandardItem(QtCore.QString(str(xCoord))),
										 QtGui.QStandardItem(QtCore.QString(str(yCoord)))])
		self.drawPoints()

		return

	def drawPoints(self):
		chosenElement = str(self.groupComboBox.currentText())
		if(chosenElement == 'All'):
			self.drawPointsForAll()
		else:
			self.drawPointsForGroup(chosenElement)
		return

	def drawPointsForAll(self):
		imagePixmap = QtGui.QPixmap('images/project.jpg')
		imagePixmap = imagePixmap.scaledToHeight(self.IMAGE_ORIGINAL_HEIGHT, 
																							QtCore.Qt.SmoothTransformation)
		painter = QtGui.QPainter(imagePixmap)
		for key in self.groups.keys():
			currentGroup = self.groups[key]
			painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2, QtCore.Qt.SolidLine))
			groupPoints = currentGroup['points']
			for i in range(0, groupPoints.rowCount()):
				xCoord = float(str(groupPoints.item(i, 3).text()))
				yCoord = float(str(groupPoints.item(i, 4).text()))
				painter.drawPoint(xCoord, yCoord)
		painter.end()
		self.image.setPixmap(imagePixmap)
		return

	def drawPointsForGroup(self, group):
		imagePixmap = QtGui.QPixmap('images/project.jpg')
		imagePixmap = imagePixmap.scaledToHeight(self.IMAGE_ORIGINAL_HEIGHT, 
																							QtCore.Qt.SmoothTransformation)
		painter = QtGui.QPainter(imagePixmap)
		currentGroup = self.groups[group]
		painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2, QtCore.Qt.SolidLine))
		groupPoints = currentGroup['points']
		for i in range(0, groupPoints.rowCount()):
			xCoord = float(str(groupPoints.item(i, 3).text()))
			yCoord = float(str(groupPoints.item(i, 4).text()))
			painter.drawPoint(xCoord, yCoord)
		painter.end()
		self.image.setPixmap(imagePixmap)
		return

	def __init__(self):
		super(CS4243Project, self).__init__()
		self.initVariables()
		self.initUI()

	def initVariables(self):
		self.screenSize = QtGui.QDesktopWidget().screenGeometry()
		self.groups = 	{
						'Group 1': {
									'direction':'None',
									'points': QtGui.QStandardItemModel(0, 5)
									}
						}
		self.groups['Group 1']['points'].itemChanged.connect(self.changeCoords)
		return

	def initUI(self):
		# Create Display Image
		self.initImage()

   		# Create Add Group Button
		self.initSideBar()

   		hbox = QtGui.QHBoxLayout()
   		hbox.addWidget(self.image)
   		hbox.addLayout(self.sideBar)
   		hbox.setSpacing(0)
   		hbox.setMargin(0)
   		hbox.setAlignment(QtCore.Qt.AlignLeft)

   		self.setLayout(hbox)
   		self.resize(self.screenSize.width(), self.screenSize.height())
		self.setWindowTitle('CS4243 Project')
		self.show()

	def initImage(self):
		labelImage = QtGui.QLabel()
 		imagePixmap = QtGui.QPixmap('images/project.jpg')
 		imagePixmap = imagePixmap.scaledToHeight(self.IMAGE_ORIGINAL_HEIGHT, 
 																						QtCore.Qt.SmoothTransformation)
 		labelImage.setPixmap(imagePixmap)
 		labelImage.setFixedSize(imagePixmap.size())

 		# Assign values
 		self.imageSize = QtCore.QSize(int(imagePixmap.size().width()), 
 																	int(imagePixmap.size().height()))
 		self.sideBarSize = QtCore.QSize(self.screenSize.width() - self.imageSize.width(), 
 																		self.screenSize.height())
 		self.image = labelImage
 		return

	def initSideBar(self):
		vbox = QtGui.QVBoxLayout()
		vbox.setAlignment(QtCore.Qt.AlignTop)
		vbox.setSpacing(30.0)

		# Group Selection
		groupComboBox = QtGui.QComboBox()
		groupComboBox.addItems(['Group 1', 'All'])
		groupComboBox.setMinimumWidth(self.sideBarSize.width() * 3 / 4.0)
		addButton = QtGui.QPushButton("+")
		addButton.clicked.connect(self.addButtonClicked)
		hbox = QtGui.QHBoxLayout()
		hbox.setAlignment(QtCore.Qt.AlignCenter)
		hbox.setSpacing(5.0)
		hbox.addWidget(groupComboBox)
		hbox.addWidget(addButton)
		vbox.addLayout(hbox)

		# Group Info
		groupInfo = QtGui.QVBoxLayout()
		groupInfo.setSpacing(10.0)
		groupInfo.setAlignment(QtCore.Qt.AlignTop)
		vbox.addLayout(groupInfo)

		#Assign variables
		self.sideBar = vbox
		self.groupComboBox = groupComboBox
		self.groupComboBox.currentIndexChanged['int'].connect(self.updateGroup)
		self.updateGroup(0)
		return

	###########################################################
	#                   MAIN LOGIC FUNCTION                   #		
	##########################################################
	def generateButtonClicked(self):
		isTestingLayout = False
		isGeneratingVideo = True
		current_milli_time = lambda: int(round(time.time() * 1000))
		groupsData = {}
		
		############################
		# 			PRE-PROCESS      	 #		
		############################
		for key in self.groups.keys():
			groupsData[key] = {}
			data = groupsData[key]
			group = self.groups[key]
			data['direction'] = group['direction']
			data['points'] = []
			data['2Dpoints'] = []
			groupPoints = group['points']
			for i in range(groupPoints.rowCount()):
				xCoord = int(str(groupPoints.item(i, 0).text())) 
				yCoord = self.IMAGE_ORIGINAL_HEIGHT - int(str(groupPoints.item(i, 1).text())) 
				zCoord = int(str(groupPoints.item(i, 2).text()))
				uCoord = int(str(groupPoints.item(i, 3).text()))
				vCoord = int(str(groupPoints.item(i, 4).text()))
				data['points'].append((xCoord, yCoord, zCoord))
				data['2Dpoints'].append((uCoord, vCoord))

		############################
		# 			INTERPOLATION      #		
		############################
		start = current_milli_time()
		pointsInterpolator = PointsInterpolator(isTestingLayout)
		interpolatedData = pointsInterpolator.interpolate(groupsData)
		print 'Time taken for interpolation: ', (current_milli_time() - start), 'ms'

		############################
		# 			FILL COLOR      	 #		
		############################
		start = current_milli_time()
		perspectiveProjector = PerspectiveProjector(isTestingLayout)
		cameraPosition = [self.IMAGE_ORIGINAL_WIDTH * 1 / 2.0, 
											self.IMAGE_ORIGINAL_HEIGHT * 9 / 10.0, 
											0]
		orientation = [	[1, 0, 0], 
										[0, 1, 0], 
										[0, 0, 1]	]
		if isTestingLayout:
			perspectiveProjector.testAlignmentByUsingDefaultColor(interpolatedData)
		else: 
			perspectiveProjector.fillColor(interpolatedData, cameraPosition, orientation)
		print 'Time taken for filling color: ', (current_milli_time() - start), 'ms'

		if not isGeneratingVideo:
			########################################
			# 			PERSPECTIVE PROJECTION      	 #		
			########################################
			start = current_milli_time()
			cameraPosition = [self.IMAGE_ORIGINAL_WIDTH * 1 / 2.0, 
												self.IMAGE_ORIGINAL_HEIGHT * 9 / 10.0, 
												0] 
			if(not isTestingLayout):
				results = perspectiveProjector.performPerspective(copy.copy(interpolatedData), 
																													cameraPosition, 
																													orientation )
			else:
				results = perspectiveProjector.performPerspectiveWithYRotatedAngle(
																												copy.copy(interpolatedData), 
																												cameraPosition, 
																												0)
			print 'Time taken for perspective projection: ', (current_milli_time() - start), 'ms'
			
			########################################
			#							FRAME DISPLAY      	 		 #		
			########################################
			imageFrame = cv2.imread('images/skyTexture.jpg')
			imageFrame = np.zeros((int(self.IMAGE_ORIGINAL_HEIGHT),int(self.IMAGE_ORIGINAL_WIDTH),3), np.uint8)
			imageFrame = cv2.resize(imageFrame, (800, 600))
			for point, color in results.iteritems():
				x = int(point[0] + self.IMAGE_ORIGINAL_WIDTH  / 2.0)
				y = int(point[1] + self.IMAGE_ORIGINAL_HEIGHT / 2.0)
				if(0 <= x and x < self.IMAGE_ORIGINAL_WIDTH 
									and 0 <= y 
									and y < self.IMAGE_ORIGINAL_HEIGHT):
					imageFrame[y][x] = [color[0], color[1], color[2]]
		
			winname = "imageWin"
			win = cv.NamedWindow(winname, cv.CV_WINDOW_AUTOSIZE)
			imageFrame = cv2.resize(imageFrame, (800, 600))
			cv2.imshow('imageWin', imageFrame)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
			cv2.imwrite('result.jpg', imageFrame)
		else:
			########################################
			# 					VIDEO GENERATOR      	 		 #			
			########################################
			videoGenerator = VideoGenerator()
			pathGenerator = CameraPathGenerator()
			generatedPath = pathGenerator.generateCameraPath()
			generatedFrames = []
			index = 1
			for point in generatedPath:
				results = perspectiveProjector.performPerspective(copy.copy(interpolatedData), 
																													point[0], 
																													point[1])
				imageFrame = cv2.imread('images/skyTexture.jpg')
				imageFrame = cv2.resize(imageFrame, (800, 600))
				for point, color in results.iteritems():
					x = int(point[0] + self.IMAGE_ORIGINAL_WIDTH  / 2.0)
					y = int(point[1] + self.IMAGE_ORIGINAL_HEIGHT / 2.0)
					if(0 <= x and x < self.IMAGE_ORIGINAL_WIDTH and 0 <= y and y < self.IMAGE_ORIGINAL_HEIGHT):
						imageFrame[y][x] = [color[0], color[1], color[2]]
				generatedFrames.append(imageFrame)
				print "Successfully generate frame ", index
				index += 1
			print "Please choose your preferences of codec (if necessary) :)"
			videoGenerator.generateVideo(generatedFrames)

		return

	def updateGroup(self, changedIndex):
		# Clear group info
		groupInfo = self.sideBar.itemAt(1)
		self.clearLayout(groupInfo)

		if(str(self.groupComboBox.currentText()) != 'All'):
			currentGroup = self.groups[str(self.groupComboBox.currentText())]

			# Add direction
			hbox = QtGui.QHBoxLayout()
			hbox.addWidget(QtGui.QLabel("Direction: "))
			directionComboBox = QtGui.QComboBox()
			directionComboBox.addItems(self.DIRECTIONS)
			directionComboBox.setCurrentIndex(directionComboBox.findText(currentGroup['direction']))
			directionComboBox.currentIndexChanged['int'].connect(self.updateDirection)
			hbox.addWidget(directionComboBox)
			groupInfo.addLayout(hbox)

			# Add points
			model = currentGroup['points']
			model.setHorizontalHeaderLabels(QtCore.QStringList(['X', 'Y', 'Z', 'u', 'v']))
			table = QtGui.QTableView()
			table.setModel(model)
			table.verticalHeader().setVisible(False)
			table.setMaximumHeight((2.5/4.0) * self.sideBarSize.height())
			table.setMinimumWidth(self.sideBarSize.width() - 15)
			for i in range(5):
				table.setColumnWidth(i, self.sideBarSize.width() / 5.0 - 1)
			groupInfo.addWidget(table)

		# Process Button
		processButton = QtGui.QPushButton("Generate Video")
		processButton.clicked.connect(self.generateButtonClicked)
		groupInfo.addWidget(processButton)

		saveButton = QtGui.QPushButton("Save group")
		saveButton.clicked.connect(self.save)
		groupInfo.addWidget(saveButton)

		loadButton = QtGui.QPushButton("Load group")
		loadButton.clicked.connect(self.load)
		groupInfo.addWidget(loadButton)
		self.drawPoints()

		return

	def load(self):
		selection = str(self.groupComboBox.currentText())
		if(selection == 'All'):
			self.loadForAllGroups()
		else:
			currentGroup = self.groups[selection]
			self.loadGroup(currentGroup)

	def loadForAllGroups(self):
		self.groupComboBox.currentIndexChanged['int'].disconnect(self.updateGroup)
		dataGenerator = DataGenerator()
		allData = dataGenerator.loadDataFromFile('data/allData.json')
		numGroups = len(allData.keys())
		self.groupComboBox.clear()
		for i in range(numGroups):
			self.groupComboBox.addItem('Group ' + str(i + 1))
		self.groupComboBox.addItem('All')
		self.groupComboBox.setCurrentIndex(self.groupComboBox.count() - 1)
		self.groups.clear()
		for group, data in allData.iteritems():
			self.groups[group] = {}
			groupData = self.groups[group]
			groupData['direction'] = data['direction']
			groupData['points'] = QtGui.QStandardItemModel(0, 3)
			for i in range(len(data['points'])):
				row = []
				xCoord = data['points'][i][0]
				yCoord = data['points'][i][1]
				zCoord = data['points'][i][2]
				uCoord = data['2Dpoints'][i][0]
				vCoord = data['2Dpoints'][i][1]
				groupData['points'].appendRow(
										[	QtGui.QStandardItem(QtCore.QString(str(xCoord))),
											QtGui.QStandardItem(QtCore.QString(str(yCoord))),
											QtGui.QStandardItem(QtCore.QString(str(zCoord))),
											QtGui.QStandardItem(QtCore.QString(str(uCoord))),
											QtGui.QStandardItem(QtCore.QString(str(vCoord)))])
				groupData['points'].itemChanged.connect(self.changeCoords)
		self.groupComboBox.currentIndexChanged['int'].connect(self.updateGroup)
		self.drawPoints()

	def loadGroup(self, currentGroup):
		dataGenerator = DataGenerator()
		data = dataGenerator.loadDataFromFile('data/groupData.json')
		self.groups[str(self.groupComboBox.currentText())]['direction'] = data['direction']
		self.groups[str(self.groupComboBox.currentText())]['points'].clear()
		for i in range(len(data['points'])):
			row = []
			xCoord = data['points'][i][0]
			yCoord = data['points'][i][1]
			zCoord = data['points'][i][2]
			uCoord = data['2Dpoints'][i][0]
			vCoord = data['2Dpoints'][i][1]
			self.groups[str(self.groupComboBox.currentText())]['points'].appendRow(
									[	QtGui.QStandardItem(QtCore.QString(str(xCoord))),
										QtGui.QStandardItem(QtCore.QString(str(yCoord))),
										QtGui.QStandardItem(QtCore.QString(str(zCoord))),
										QtGui.QStandardItem(QtCore.QString(str(uCoord))),
										QtGui.QStandardItem(QtCore.QString(str(vCoord)))])

		self.drawPoints()

	def save(self):
		selection = str(self.groupComboBox.currentText())
		if(selection == 'All'):
			self.saveForAllGroups()
		else:
			currentGroup = self.groups[selection]
			self.saveGroup(currentGroup)

	def saveGroup(self, currentGroup):
		savedPoints = []
		saved2DPoints = []
		for i in range(currentGroup['points'].rowCount()):
			xCoord = int(str(currentGroup['points'].item(i, 0).text())) 
			yCoord = int(str(currentGroup['points'].item(i, 1).text())) 
			zCoord = int(str(currentGroup['points'].item(i, 2).text()))
			savedPoints.append((xCoord, yCoord, zCoord))
			uCoord = int(str(currentGroup['points'].item(i, 3).text())) 
			vCoord = int(str(currentGroup['points'].item(i, 4).text())) 
			saved2DPoints.append((uCoord, vCoord))

		group = {	'direction' : currentGroup['direction'], 
							'points' : savedPoints, 
							'2Dpoints': saved2DPoints
						}

		dataGenerator = DataGenerator()
		dataGenerator.saveDataToFile('data/groupData.json',group)

	def saveForAllGroups(self):
		groupsData = {}
		for key in self.groups.keys():
			groupsData[key] = {}
			data = groupsData[key]
			group = self.groups[key]
			data['direction'] = group['direction']
			data['2Dpoints'] = []
			data['points'] = []
			groupPoints = group['points']
			for i in range(groupPoints.rowCount()):
				xCoord = int(str(groupPoints.item(i, 0).text()))
				yCoord = int(str(groupPoints.item(i, 1).text())) 
				zCoord = int(str(groupPoints.item(i, 2).text()))
				data['points'].append((xCoord, yCoord, zCoord))
				uCoord = int(str(groupPoints.item(i, 3).text()))
				vCoord = int(str(groupPoints.item(i, 4).text()))
				data['2Dpoints'].append((uCoord, vCoord))
				
		dataGenerator = DataGenerator()
		dataGenerator.saveDataToFile('data/allData.json', groupsData)


	def updateDirection(self, changedIndex):
		currentGroup = self.groups[str(self.groupComboBox.currentText())]
		currentGroup['direction'] = self.DIRECTIONS[changedIndex]
		return

	def clearLayout(self, layout):
	    if layout is not None:
	        while layout.count():
	            item = layout.takeAt(0)
	            widget = item.widget()
	            if widget is not None:
	                widget.deleteLater()
	            else:
	                self.clearLayout(item.layout())

	def addButtonClicked(self):
		numItems = self.groupComboBox.count()
		self.groupComboBox.insertItem(self.groupComboBox.count() - 1, 
																	'Group ' + str(numItems))
		self.groups['Group ' + str(numItems)] = {	
																							'direction': 'None', 
																							'points': QtGui.QStandardItemModel(0, 5)
																						}
		self.groups['Group ' + str(numItems)]['points'].itemChanged.connect(self.changeCoords)
		return

	def changeCoords(self, item):
		self.drawPoints()
		return


def main():
	print "Open application..."
	app = QtGui.QApplication(sys.argv)
	view = CS4243Project()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()