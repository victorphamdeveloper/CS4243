import sys
import cv2 as cv
import numpy as np
import numpy.linalg as la
import copy

# This class is used for generating video
class VideoGenerator:
    def __init__(self):
        print "Initialize Video Generator Process"
        return

    def videoGeneration(total, width, height):

        #the second parameters -1 is the codec
        #need more research on the codec, but -1 works on my computer
        video = cv.VideoWriter("video.avi", -1, 1, (width, height))
        
        #total is the total number of images
        #here we assume all the images have the same witdh and same height
        #so, the width and the height can be obtained through the first image
        #e.g., using .shape

        #read through 0.jpg to total.jpg
        for n in range(0,total):
            video.write(cv.imread((str(total)) + ".jpg"))

        cv.destroyAllWindows()
        video.release()
