from __future__ import division

import cv2
import cv2.cv as cv
import numpy as np
import math

class cameraPathGenerator:
    def __init__(self):
        return
    
    """
    Find camera positions and angles
    * resultput format:
        [((position1.x, position1.y, position1.z), (orientation1.x, orientation1.y, orientation1.z)),
         ((position2.x, position2.y, position2.z), (orientation2.x, orientation2.y, orientation2.z)),...]
    """
    def generateCameraPath(self):
        keyPoints = [ ((158, 5, 10), -30), 
                      ((1316, 6, 8), 120), 
                      ((688, 8, 5), 90), 
                      ((940, 6, 3), 100)]
        step = 50
        angleMove = 10
        generatedPoints = []
        
        keyX = [int(point[0]) for (point, angle) in keyPoints]
        keyY = [int(point[1]) for (point, angle) in keyPoints]
        keyZ = [int(point[2]) for (point, angle) in keyPoints]
        keyAngles= [angle for (point, angle) in keyPoints]
        
        angle = keyAngles[0]
        for i in range(len(keyPoints) - 1):
            x = keyX[i]
            y = keyY[i] 
            z = keyZ[i]

            # Gradually rotate to initial angle
            if (angle < keyAngles[i]):
                while (angle < keyAngles[i]):
                    angle += angleMove
                    quatMat = self._angleToQuatMat(angle)
                    generatedPoints.append(((x, y, z), quatMat))
            else:
                while (angle > keyAngles[i]):
                    angle -= angleMove
                    quatMat = self._angleToQuatMat(angle)
                    generatedPoints.append(((x, y, z), quatMat))
            
            # Interpolate x and angle
            signedStep = step
            if keyX[i] > keyX[i+1]:
                signedStep = -step
                
            signedAngleMove = angleMove
            if keyAngles[i] > keyAngles[i+1]:
                signedAngleMove = -angleMove
            
            dx = keyX[i+1] - keyX[i]
            dy = keyY[i+1] - keyY[i]
            dz = keyZ[i+1] - keyZ[i]
            slopeZ = dz / dx
            slopeY = dy / dx 
            
            while x == keyX[i] or (x - keyX[i])*(x - keyX[i+1]) < 0:
                z = int(keyZ[i] + (x - keyX[i]) * slopeZ)
                y = int(keyY[i] + (x - keyX[i]) * slopeY)
                quatMat = self._angleToQuatMat(angle)
                generatedPoints.append(((x, y, z), quatMat)) 
                
                x += signedStep
                angle += signedAngleMove
                
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
    