# System Dependence
from sys import platform as _platform

# External Dependence
import cv2.cv as cv
import cv2

###########################################################
#                   Video Generator                       #
###########################################################
class VideoGenerator:
    NUM_FRAMES_PER_SECONDS = 25
    FRAME_WIDTH = 800
    FRAME_HEIGHT = 600

    def __init__(self):
        print "Initialize Video Generator Process"
        return

    def generateVideo(self, frames):
        # Initialize Video Writer
        if _platform == "linux" or _platform == "linux2":
            fourcc = cv.CV_FOURCC('m', 'p', '4', 'v')
        elif _platform == "darwin":
            fourcc = cv.CV_FOURCC('m', 'p', '4', 'v')
        elif _platform == "win32":
            fourcc = -1

        videoWriter = cv2.VideoWriter("FlyThroughResult.avi", fourcc, 
                                self.NUM_FRAMES_PER_SECONDS, 
                                (self.FRAME_WIDTH, self.FRAME_HEIGHT))
        for imageFrame in frames:
            videoWriter.write(imageFrame)
        videoWriter.release()
        videoWriter = None