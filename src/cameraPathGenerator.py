# System Dependence
from __future__ import division
import math

# External Dependence
import cv2
import cv2.cv as cv
import numpy as np
import numpy.linalg as la

###########################################################
#                   Camera Path Generator                 #
###########################################################
class CameraPathGenerator:
    NUM_FRAMES = 50
    IMAGE_ORIGINAL_WIDTH = 800
    IMAGE_ORIGINAL_HEIGHT = 600

    def __init__(self):
        return
    
    """
    Find camera positions and angles
    * resultput format:
        [((position1.x, position1.y, position1.z), (orientation1.x, orientation1.y, orientation1.z)),
         ((position2.x, position2.y, position2.z), (orientation2.x, orientation2.y, orientation2.z)),...]
    """
    def generateCameraPath(self):
        point1 = ((self.IMAGE_ORIGINAL_WIDTH * 2.5 / 5.0, 
                   self.IMAGE_ORIGINAL_HEIGHT * 7.75 / 10.0, 
                   0), 0)
        point2 = ((self.IMAGE_ORIGINAL_WIDTH * 3 / 5.0, 
                   self.IMAGE_ORIGINAL_HEIGHT * 9 / 10.0, 
                   200), np.pi / 12.0)
        point3 = ((self.IMAGE_ORIGINAL_WIDTH * 2.5 / 5.0, 
                   self.IMAGE_ORIGINAL_HEIGHT * 9 / 10.0, 
                   400), 0)
        point4 = ((self.IMAGE_ORIGINAL_WIDTH * 2 / 5.0, 
                   self.IMAGE_ORIGINAL_HEIGHT * 9 / 10.0, 
                   600), -np.pi / 6.0)
        keyPointsAndAngles = [point1, point2, point3, point4]
        generatedPoints = []
        
        numKeys = len(keyPointsAndAngles)
        keyPoints = [point for (point, angle) in keyPointsAndAngles]
        keyAngles= [angle for (point, angle) in keyPointsAndAngles]
        keyX = [point[0] for point in keyPoints]
        keyY = [point[1] for point in keyPoints]
        keyZ = [point[2] for point in keyPoints]
        
        # Calculate step length of camera path
        totalLength = 0
        framesCount = []
        for i in range(numKeys - 1):
            count = 0
            length = la.norm(np.asarray(keyPoints[i+1]) - np.asarray(keyPoints[i]))
            totalLength += length
            count += int(self.NUM_FRAMES / (numKeys - 1))
            if(i == numKeys - 2):
                count += self.NUM_FRAMES % (numKeys - 1)
            framesCount.append(count)
            
        # Generate camera path            
        for i in range(numKeys - 1):
            numFrames = framesCount[i]
            currentX = keyX[i]
            nextX = keyX[i+1]
            currentY = keyY[i] 
            nextY = keyY[i+1]
            currentZ = keyZ[i]
            nextZ = keyZ[i+1]
            currentAngle = keyAngles[i]
            nextAngle = keyAngles[i+1]
            
            step = 1.0 / (numFrames)
            for i in range(numFrames):
                ratio = step * i
                interpolatedX = currentX * (1 - ratio) + ratio * nextX
                interpolatedY = currentY * (1 - ratio) + ratio * nextY
                interpolatedZ = currentZ * (1 - ratio) + ratio * nextZ
                angle = currentAngle + ratio * (nextAngle - currentAngle)
                quatMat = self._angleToQuatMat(angle)
                generatedPoints.append(((interpolatedX, interpolatedY, interpolatedZ), quatMat)) 

        return generatedPoints
    
    ##################### SUPPORT FUNCTIONS ##############################
    def _angleToQuatMat(self, angle):
        worldQuat = [math.cos(angle/2.0), 0, math.sin(angle/2.0), 0]
        return self._quat2rot(worldQuat)

    def _quat2rot(self, q):
        result = np.matrix(np.zeros([3,3]))
        result[0, 0] = q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3]
        result[0, 1] = 2 * (q[1] * q[2] - q[0] * q[3])
        result[0, 2] = 2 * (q[1] * q[3] + q[0] * q[2])
        result[1, 0] = 2 * (q[1] * q[2] + q[0] * q[3])
        result[1, 1] = q[0] * q[0] + q[2] * q[2] - q[1] * q[1] - q[3] * q[3]
        result[1, 2] = 2 * (q[2] * q[3] - q[0] * q[1])
        result[2, 0] = 2 * (q[1] * q[3] - q[0] * q[2])
        result[2, 1] = 2 * (q[2] * q[3] + q[0] * q[1])
        result[2, 2] = q[0] * q[0] + q[3] * q[3] - q[1] * q[1] - q[2] * q[2]

        return result
    