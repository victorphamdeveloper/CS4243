import json
from pprint import pprint
import codecs

#This class is used for generating test data instead of
#having to create data through the interface repeatedly
class DataGenerator:
	def __init__(self):
		print "Create DataGenerator object"
		return

	def initializeData(self):
		print "Initialize data for testing"
		return

	def generateData():
		return

	def saveDataToFile(self, fileName, groups):
		with open(fileName, 'w') as outfile:
			json.dump(groups, outfile)
			
	def loadDataFromFile(self, fileName):
		input_file  = file(fileName, "r")
		data = json.loads(input_file.read().decode("utf-8-sig"))
		return data
		
	def test(self):
		print 'in DataGenerator'