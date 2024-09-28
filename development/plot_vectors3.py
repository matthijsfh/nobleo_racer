from typing import Tuple
import sys
sys.path.append("../../..")
from linear_math import Transform
import os
from pygame import Vector2
import pygame
import math
import itertools
import numpy as np
import matplotlib.pyplot as plt


track_lines = [
    Vector2(1389.2, 440.844), Vector2(1466.64, 452.317), Vector2(1518.27, 497.253), Vector2(1524, 556.531), 
    Vector2(1487.67, 628.237), Vector2(1375.81, 692.295), Vector2(1235.27, 743.924), Vector2(800.246, 854.83), 
    Vector2(405.381, 919.844), Vector2(262.924, 894.03), Vector2(205.559, 829.972), Vector2(211.295, 782.168), 
    Vector2(272.485, 764.002), Vector2(620.501, 769.738), Vector2(802.158, 742.968),Vector2 (848.05, 711.417), 
    Vector2(872.908, 643.535), Vector2(865.26, 575.653), Vector2(820.324, 528.804),Vector2(775.387, 509.683), 
    Vector2(159.667, 445.625), Vector2(97.521, 406.425), Vector2(71.7066, 336.631), Vector2(87.004, 276.397), 
    Vector2(132.896, 232.417), Vector2(210.339, 219.032), Vector2(482.824, 243.89), Vector2(566.96, 227.637), 
    Vector2(768.695, 89.0038), Vector2(833.709, 75.6186), Vector2(925.493, 88.0477),Vector2(1219.97, 193.217), 
    Vector2(1373.9, 220.944), Vector2(1419.79, 205.647), Vector2(1562.25, 117.686), Vector2(1642.56, 97.6086), 
    Vector2(1746.77, 111.95), Vector2(1818.48, 174.096), Vector2(1829.95, 240.066), Vector2(1792.67, 275.441), 
    Vector2(1681.76, 283.09), Vector2(760.09, 281.177), Vector2(678.823, 309.86), Vector2(640.579, 351.928), 
    Vector2(650.14, 395.908), Vector2(716.11, 429.371), Vector2(828.928, 444.669)
]

class Track():
    def __init__(self):
        self.lines= []
    
    

class Testing():
    def __init__(self):
        
        self.track = Track()
        self.track.lines = track_lines
        
        #----------------------------------------------------------------------
        # Orginele baan
        #----------------------------------------------------------------------
        # All coordinates including last one + list + next one.
        self.sectionCount = len(self.track.lines)

        # Dus 2 langer dan sectionCount
        # self.coordinates = [self.track.lines[-1]] + self.track.lines + [self.track.lines[0]]
        # Dus 1 langer dan sectionCount
        # self.relativeVectors = [c1 - c0 for c0, c1 in itertools.pairwise(self.coordinates)]

        self.coordinates = self.track.lines + [self.track.lines[0]]
        self.relativeVectors = [c1 - c0 for c0, c1 in itertools.pairwise(self.coordinates)]
        
        # Calculate angles for each section
        self.absAngles = [math.degrees(math.atan2(y, x)) for x, y in self.relativeVectors]
        
        self.myNewCoordinates = [self.coordinates[i] for i in range(len(self.coordinates))]
        
        print(len(self.coordinates))
        print(len(self.relativeVectors))
        
        return

    
    def bochtenAfsnijden(self):
        for i in range(0, self.sectionCount):
    
            # print(track_lines[i])
            # print (relativeVectors[i])
        
            lengte1 = self.relativeVectors[(i-1) % self.sectionCount].length()
            lengte2 = self.relativeVectors[(i+0) % self.sectionCount].length()
            
            magic = 100
        
            # Calculate new point on the line close to the exit
            newPoint1 = Vector2(self.relativeVectors[(i-1) % self.sectionCount] * (1 -magic / lengte1) + self.track.lines[(i-1) % (self.sectionCount)])
            newPoint2 = Vector2(self.relativeVectors[(i+0) % self.sectionCount] * (magic / lengte2)  + self.track.lines[i])
    
            self.curve = self.bezier_curve(newPoint1, self.track.lines[i], newPoint2, 3)
            
            # print(newPoint1)
            # print(self.track.lines[i])
            # print(newPoint2)
            # print(self.curve)
            
            tmp = Vector2(self.curve[1][0], self.curve[1][1])
            
            # Only cut sharp corners.

            relativeAngle1 = self.absAngles[(i-0) % self.sectionCount] - self.absAngles[(i-1) % self.sectionCount]
            relativeAngle2 = self.absAngles[(i+1) % self.sectionCount] - self.absAngles[(i-0) % self.sectionCount]
            relativeAngle3 = self.absAngles[(i+2) % self.sectionCount] - self.absAngles[(i+1) % self.sectionCount]

            print(f"i = {i}, hoek = {relativeAngle1}, {relativeAngle2}")

            if (abs(relativeAngle1) >= 5) and (abs(relativeAngle2) >= 5) and (abs(relativeAngle2) >= 5):
                # if (abs(relativeAngle1) <= 40) and (abs(relativeAngle2) <= 40) and (abs(relativeAngle3) <= 40):
                self.myNewCoordinates[i] = Vector2(tmp)
            
        return
    
    def plotCoordinates(self, fig, axis, color='grey'):
        
        tmp = self.coordinates
        
        x_vals = [v[0] for v in tmp]
        y_vals = [-1*v[1] for v in tmp]
        
        axis.plot(x_vals, y_vals, marker='o', color=color)
        axis.grid(True)
        
        return

    def plotCoordinates2(self, fig, axis, color='grey'):
        
        tmp = self.myNewCoordinates
        
        x_vals = [v[0] for v in tmp]
        y_vals = [-1*v[1] for v in tmp]
        
        axis.plot(x_vals, y_vals, marker='o', color=color)
        axis.grid(True)
        
        return

    
    # def plotRelativeVectors(self, fig, axis, relativeVectors, marker=''):
    #     x_vals = [v[0] for v in relativeVectors]
    #     y_vals = [-1*v[1] for v in relativeVectors]
        
    #     axis.plot(x_vals, y_vals, marker=marker)
    #     axis.grid(True)
    
    #     return
    
    
    # def plotPoint(self, fig, axis, point: Vector2,  marker="*", color="Orange"):
    #     axis.scatter(point.x, -1.0*point.y, marker='*', color=color)
    
    #     return
    
    # def plotLine(self, fig, axis, point1: Vector2, point2: Vector2, color="Orange"):
    #     axis.plot([point1.x, point2.x] , [-1.0*point1.y, -1*point2.y], -1.0*point2.y, color=color)
    
    #     return


    def bezier_curve(self, p0, p1, p2, num_points=10):
        """Generates a quadratic Bezier curve given 3 control points."""
        t = np.linspace(0, 1, num_points).reshape(-1, 1)  # Reshape to column vector
        curve = (1-t)**2 * p0 + 2*(1-t) * t * p1 + t**2 * p2
        return curve


def main():
    test = Testing()
    
    fig, axes = plt.subplots(1, 1)
    
    test.plotCoordinates(fig, axes)        
    test.bochtenAfsnijden()
    test.plotCoordinates2(fig, axes, color='blue')        
    
    
    plt.show()
        

if __name__ == '__main__':
    main()

