# System Dependence
import json
from pprint import pprint
import codecs

###########################################################
#                   Data Generator                        #
###########################################################
#This class save all data to a file for ease of adding data every time
class DataGenerator:
	def __init__(self):
		return
		
	def saveDataToFile(self, fileName, groups):
		with open(fileName, 'w') as outfile:
			json.dump(groups, outfile)

	def loadDataFromFile(self, fileName):
		input_file  = file(fileName, "r")
		data = json.loads(input_file.read().decode("utf-8-sig"))
		return data