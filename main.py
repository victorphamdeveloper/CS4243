import sys
import copy
import json
from pointsInterpolator import *
from perspectiveProjector import *
from dataGenerator import *
from PyQt4 import QtGui, QtCore

import cv2
import cv2.cv as cv
import numpy as np

class CS4243Project(QtGui.QWidget):
	# Constant Declaration
	DIRECTIONS = ["None", "North", "South", "West", "East", "Upwards", "Downwards"]
	IMAGE_ORIGINAL_WIDTH = 1632.0
	IMAGE_ORIGINAL_HEIGHT = 1224.0

	def mousePressEvent(self, event):
		super(CS4243Project, self).mousePressEvent(event)
		xCoord = event.x()
		yCoord = event.y()
		if(xCoord > self.imageSize.width()):
			return
		currentGroup = self.groups[str(self.groupComboBox.currentText())]
		currentGroup['points'].appendRow([QtGui.QStandardItem(QtCore.QString(str(xCoord))),
										QtGui.QStandardItem(QtCore.QString(str(yCoord))),
										QtGui.QStandardItem(QtCore.QString(str(0)))])
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
		imagePixmap = QtGui.QPixmap('project.jpg')
   		imagePixmap = imagePixmap.scaledToHeight(self.screenSize.height(), QtCore.Qt.SmoothTransformation)
		painter = QtGui.QPainter(imagePixmap)
		for key in self.groups.keys():
			currentGroup = self.groups[key]
			painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2, QtCore.Qt.SolidLine))
			groupPoints = currentGroup['points']
			for i in range(0, groupPoints.rowCount()):
				xCoord = float(str(groupPoints.item(i, 0).text()))
				yCoord = float(str(groupPoints.item(i, 1).text()))
				painter.drawPoint(xCoord, yCoord)
		painter.end()
		self.image.setPixmap(imagePixmap)
		return

	def drawPointsForGroup(self, group):
		imagePixmap = QtGui.QPixmap('project.jpg')
   		imagePixmap = imagePixmap.scaledToHeight(self.screenSize.height(), QtCore.Qt.SmoothTransformation)
		painter = QtGui.QPainter(imagePixmap)
		currentGroup = self.groups[group]
		painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2, QtCore.Qt.SolidLine))
		groupPoints = currentGroup['points']
		for i in range(0, groupPoints.rowCount()):
			xCoord = float(str(groupPoints.item(i, 0).text()))
			yCoord = float(str(groupPoints.item(i, 1).text()))
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
									'points': QtGui.QStandardItemModel(0, 3)
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
   		imagePixmap = QtGui.QPixmap('project.jpg')
   		imagePixmap = imagePixmap.scaledToHeight(self.screenSize.height(), QtCore.Qt.SmoothTransformation)
   		labelImage.setPixmap(imagePixmap)
   		labelImage.setFixedSize(imagePixmap.size())

   		# Assign values
   		self.imageSize = imagePixmap.size()
   		self.sideBarSize = QtCore.QSize(self.screenSize.width() - self.imageSize.width(), self.screenSize.height())
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

	# Main function to intialize the processing logic
	def generateButtonClicked(self):
		groupsData = {}
		for key in self.groups.keys():
			groupsData[key] = {}
			data = groupsData[key]
			group = self.groups[key]
			data['direction'] = group['direction']
			data['points'] = []
			groupPoints = group['points']
			for i in range(groupPoints.rowCount()):
				xCoord = int(str(groupPoints.item(i, 0).text())) * self.IMAGE_ORIGINAL_WIDTH / self.imageSize.width()
				yCoord = int(str(groupPoints.item(i, 1).text())) * self.IMAGE_ORIGINAL_HEIGHT / self.imageSize.height()
				zCoord = int(str(groupPoints.item(i, 2).text()))
				data['points'].append((xCoord, yCoord, zCoord))

		pointsInterpolator = PointsInterpolator()
		interpolatedData = pointsInterpolator.interpolate(groupsData)

		perspectiveProjector = PerspectiveProjector()
		cameraPosition = [self.IMAGE_ORIGINAL_WIDTH / 2.0, self.IMAGE_ORIGINAL_HEIGHT / 2.0, -5]
		orientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
		results = perspectiveProjector.performPerspective(copy.deepcopy(interpolatedData), cameraPosition, orientation )

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
			model.setHorizontalHeaderLabels(QtCore.QStringList(['X', 'Y', 'Z']))
			table = QtGui.QTableView()
			table.setModel(model)
			table.verticalHeader().setVisible(False)
			table.setMaximumHeight((2.5/4.0) * self.sideBarSize.height())
			table.setMinimumWidth(self.sideBarSize.width() - 15)
			for i in range(3):
				table.setColumnWidth(i, self.sideBarSize.width() / 3.0 - 5)
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
		allData = dataGenerator.loadDataFromFile('allData.json')
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
				xCoord = int(xCoord * self.imageSize.width() / self.IMAGE_ORIGINAL_WIDTH)
				yCoord = data['points'][i][1]
				yCoord = int(yCoord * self.imageSize.height() / self.IMAGE_ORIGINAL_HEIGHT)
				zCoord = data['points'][i][2]
				groupData['points'].appendRow([QtGui.QStandardItem(QtCore.QString(str(xCoord))),
										QtGui.QStandardItem(QtCore.QString(str(yCoord))),
										QtGui.QStandardItem(QtCore.QString(str(zCoord)))])
			groupData['points'].itemChanged.connect(self.changeCoords)
		self.groupComboBox.currentIndexChanged['int'].connect(self.updateGroup)
		self.drawPoints()

	def loadGroup(self, currentGroup):
		dataGenerator = DataGenerator()
		data = dataGenerator.loadDataFromFile('groupData.json')
		self.groups[str(self.groupComboBox.currentText())]['direction'] = data['direction']
		self.groups[str(self.groupComboBox.currentText())]['points'].clear()
		for i in range(len(data['points'])):
			row = []
			xCoord = data['points'][i][0]
			xCoord = int(xCoord * self.imageSize.width() / self.IMAGE_ORIGINAL_WIDTH)
			yCoord = data['points'][i][1]
			yCoord = int(yCoord * self.imageSize.height() / self.IMAGE_ORIGINAL_HEIGHT)
			zCoord = data['points'][i][2]
			self.groups[str(self.groupComboBox.currentText())]['points'].appendRow([QtGui.QStandardItem(QtCore.QString(str(xCoord))),
									QtGui.QStandardItem(QtCore.QString(str(yCoord))),
									QtGui.QStandardItem(QtCore.QString(str(zCoord)))])
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
		for i in range(currentGroup['points'].rowCount()):
			xCoord = int(str(currentGroup['points'].item(i, 0).text())) * self.IMAGE_ORIGINAL_WIDTH / self.imageSize.width()
			yCoord = int(str(currentGroup['points'].item(i, 1).text())) * self.IMAGE_ORIGINAL_HEIGHT / self.imageSize.height()
			zCoord = int(str(currentGroup['points'].item(i, 2).text()))
			savedPoints.append((xCoord, yCoord, zCoord))

		group = {'direction' : currentGroup['direction'], 'points' : savedPoints}

		dataGenerator = DataGenerator()
		dataGenerator.saveDataToFile('groupData.json',group)

	def saveForAllGroups(self):
		groupsData = {}
		for key in self.groups.keys():
			groupsData[key] = {}
			data = groupsData[key]
			group = self.groups[key]
			data['direction'] = group['direction']
			data['points'] = []
			groupPoints = group['points']
			for i in range(groupPoints.rowCount()):
				xCoord = int(str(groupPoints.item(i, 0).text())) * self.IMAGE_ORIGINAL_WIDTH / self.imageSize.width()
				yCoord = int(str(groupPoints.item(i, 1).text())) * self.IMAGE_ORIGINAL_HEIGHT / self.imageSize.height()
				zCoord = int(str(groupPoints.item(i, 2).text()))
				data['points'].append((xCoord, yCoord, zCoord))

		dataGenerator = DataGenerator()
		dataGenerator.saveDataToFile('allData.json', groupsData)


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
		self.groupComboBox.insertItem(self.groupComboBox.count() - 1, 'Group ' + str(numItems))
		self.groups['Group ' + str(numItems)] = {'direction': 'None', 'points': QtGui.QStandardItemModel(0, 3)}
		self.groups['Group ' + str(numItems)]['points'].itemChanged.connect(self.changeCoords)
		return

	def changeCoords(self, item):
		self.drawPoints()
		return


def main():
	app = QtGui.QApplication(sys.argv)
	view = CS4243Project()


	sys.exit(app.exec_())

if __name__ == '__main__':
	main()