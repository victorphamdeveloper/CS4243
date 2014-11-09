# System Dependence
import sys

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

    def generateVideo(frames):
        # Initialize Video Writer
        videoWriter = cv2.VideoWriter("FlyThroughResult.avi", -1, 
                                self.NUM_FRAMES_PER_SECONDS, 
                                (self.FRAME_WIDTH, self.FRAME_HEIGHT))

        for imageFrame in frames:
            videoWriter.write(imageFrame)

        cv2.destroyAllWindows()
        videoWriter.release()
