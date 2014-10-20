import sys
from PyQt4 import QtGui, QtCore

class CS4243Project(QtGui.QWidget):
	# Constant Declaration
	DIRECTIONS = ["North", "South", "West", "East"]

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
		imagePixmap = QtGui.QPixmap('project.jpeg')
   		imagePixmap = imagePixmap.scaledToHeight(self.screenSize.height(), QtCore.Qt.SmoothTransformation)
		painter = QtGui.QPainter(imagePixmap)
		painter.setPen(QtGui.QPen(QtCore.Qt.red, 3, QtCore.Qt.SolidLine))
		for key in self.groups.keys():
			groupPoints = self.groups[key]['points']
			for i in range(0, groupPoints.rowCount()):
				xCoord = int(str(groupPoints.item(i, 0).text()))
				yCoord = int(str(groupPoints.item(i, 1).text()))
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
									'direction':'North',
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
   		imagePixmap = QtGui.QPixmap('project.jpeg')
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

		groupComboBox = QtGui.QComboBox()
		groupComboBox.addItems(['Group 1'])
		groupComboBox.setMinimumWidth(self.sideBarSize.width() * 3 / 4.0)
		
		addButton = QtGui.QPushButton("+")
		addButton.clicked.connect(self.addButtonClicked)
		
		hbox = QtGui.QHBoxLayout()
		hbox.setAlignment(QtCore.Qt.AlignCenter)
		hbox.setSpacing(5.0)
		hbox.addWidget(groupComboBox)
		hbox.addWidget(addButton)
		
		vbox.addLayout(hbox)
		groupInfo = QtGui.QVBoxLayout()
		groupInfo.setSpacing(10.0)
		vbox.addLayout(groupInfo)

		#Assign variables
		self.sideBar = vbox
		self.groupComboBox = groupComboBox
		self.groupComboBox.currentIndexChanged['int'].connect(self.updateGroup)               
		self.updateGroup(0)
		return 

	def updateGroup(self, changedIndex):
		currentGroup = self.groups[str(self.groupComboBox.currentText())]
		
		# Clear group info
		groupInfo = self.sideBar.itemAt(1)
		self.clearLayout(groupInfo)

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
		for i in range(3):
			table.setColumnWidth(i, self.sideBarSize.width() / 3.0)
		groupInfo.addWidget(table)

		return

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
		self.groupComboBox.addItem('Group ' + str(numItems + 1))
		self.groups['Group ' + str(numItems + 1)] = {'direction': 'North', 'points': QtGui.QStandardItemModel(0, 3)}
		self.groups['Group ' + str(numItems + 1)]['points'].itemChanged.connect(self.changeCoords)
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