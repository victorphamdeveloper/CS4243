from __future__ import division

import cv2
import cv2.cv as cv
import numpy as np
import numpy.linalg as la
import scipy.interpolate as interpolate

class cameraPathGenerator:
    def __init__(self):
        return
    
    """
    Find camera positions and angles
    * Output format:
        [((x1, y1, z1), angle1), (x2, y2, z2), angle2),...]
    """
    def generateCameraPath(self):
        keyPoints = [ ((158, 1192, 10), -30), 
                      ((1316, 1121, 8), 120), 
                      ((688, 978, 5), 90), 
                      ((940, 958, 3), 100)]
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
                    generatedPoints.append(((x, y, z), angle))
            else:
                while (angle > keyAngles[i]):
                    angle -= angleMove
                    generatedPoints.append(((x, y, z), angle))
            
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
                generatedPoints.append(((x, y, z), angle)) 
                
                x += signedStep
                angle += signedAngleMove
                
        return generatedPoints
    