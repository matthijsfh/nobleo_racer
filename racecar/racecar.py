from ....linear_math import Transform
import math
from pygame.math import Vector2


class racecar:
    def __init__(self):
        self._position      = Transform(None, [0,0])
        self._trekhaak      = Transform(None, [0,0])
        self._oldposition   = [Vector2(0, 0) for _ in range(50)]
        return
    

    def setPosition(self, position: Transform, DEBUG = False):
        self._position = position
        
        if (DEBUG):
            print(f"RaceCar position : {self._position.p}, angle: {self._position.M.angle}")
        
        return
    
    def calculateTrekhaak(self, DEBUG = False):
        self._trekhaak.M.fromangle(0.0)
        
        self._trekhaakOffset = Vector2(-20,0)
        self._trekhaak.p = self._position.M * self._trekhaakOffset + self._position.p
        
        if (DEBUG):
            print(f"Trekhaak position: {self._trekhaak.p}, angle: {self._trekhaak.M.angle}")
        
        return
        
    def updateOldPosition(self, position: Transform, DEBUG = False):
        self._oldposition = self._oldposition[1:] + self._oldposition[:1]
        self._oldposition[-1] = Vector2(position.p)
        return
    
    def getTrekhaakPosition(self):
        return self._trekhaak.p
        
    def getRaceCarPosition(self):
        return self._position.p
    
    def getRaceCarOldPosition(self):
        return self._oldposition[0]