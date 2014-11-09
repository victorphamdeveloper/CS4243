from __future__ import division

import cv2
import cv2.cv as cv
import numpy as np
import numpy.linalg as la
import math

class cameraPathGenerator:
    NUM_FRAMES = 300
    
    def __init__(self):
        return
    
    """
    Find camera positions and angles
    * resultput format:
        [((position1.x, position1.y, position1.z), (orientation1.x, orientation1.y, orientation1.z)),
         ((position2.x, position2.y, position2.z), (orientation2.x, orientation2.y, orientation2.z)),...]
    """
    def generateCameraPath(self):
        keyPointsAndAngles = [((158, 5, 10), -30), 
                              ((1316, 6, 8), 120), 
                              ((688, 8, 5), 90), 
                              ((940, 6, 3), 100)]
        generatedPoints = []
        
        keyPoints = [point for (point, angle) in keyPointsAndAngles]
        keyAngles= [angle for (point, angle) in keyPointsAndAngles]
        keyX = [int(point[0]) for point in keyPoints]
        keyY = [int(point[1]) for point in keyPoints]
        keyZ = [int(point[2]) for point in keyPoints]
        
        # Calculate step length of camera path
        length = 0
        for i in range(len(keyPoints) - 1):
            length += la.norm(np.asarray(keyPoints[i+1]) - np.asarray(keyPoints[i]))
        
        step = length / self.NUM_FRAMES
            
        # Generate camera path            
        for i in range(len(keyPoints) - 1):
            x = keyX[i]
            y = keyY[i] 
            z = keyZ[i]
            angle = keyAngles[i]
            
            # Calculate line slopes
            xDifference = keyX[i+1] - keyX[i]
            yDifference = keyY[i+1] - keyY[i]
            zDifference = keyZ[i+1] - keyZ[i]
            slopeZ = zDifference / xDifference
            slopeY = (yDifference * yDifference) / (xDifference * zDifference) 

            # Calculate step for x
            stepX = xDifference * step / la.norm(np.asarray(keyPoints[i+1]) - np.asarray(keyPoints[i]))
            if xDifference % stepX == 0:
                numX = int(xDifference / stepX)
            else:
                numX = int(xDifference / stepX) + 1 
            
            # Calculate angle move
            angleMove = (keyAngles[i+1] - keyAngles[i]) / numX
            
            # Interpolate x and angle
            while x == keyX[i] or (x - keyX[i])*(x - keyX[i+1]) < 0:
                z = int(keyZ[i] + (x - keyX[i]) * slopeZ)
                y = int(keyY[i] + np.sqrt((x - keyX[i]) * (z - keyZ[i]) * slopeY))
                quatMat = self._angleToQuatMat(angle)
                generatedPoints.append(((x, y, z), quatMat)) 
                
                x += stepX
                angle += angleMove
                
        return generatedPoints
    
    ##################### SUPPORT FUNCTIONS ##############################
    def _angleToQuatMat(self, angle):
        worldQuat = [math.cos(-angle/2), 0, math.sin(-angle/2), 0]
        initialQuatMat = np.matrix(np.identity(3))
        rotatedQuatMat = initialQuatMat * self._quat2rot(worldQuat)
        
        return rotatedQuatMat

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
    