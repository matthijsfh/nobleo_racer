from ....linear_math import Transform
import math
from pygame.math import Vector2


class racecar:
    def __init__(self):
        self._position = Transform(None, [0,0])
        self._trekhaak = Transform(None, [0,0])

        return
    

    def setPosition(self, position: Transform):
        self._position = position
        
        print(f"RaceCar position : {self._position.p}, angle: {self._position.M.angle}")
        
        return
    
    def calculateTrekhaak(self):
        self._trekhaak.M.fromangle(0.0)
        
        self._trekhaakOffset = Vector2(-25,0)
        self._trekhaak.p = self._position.M * self._trekhaakOffset + self._position.p
        
        print(f"Trekhaak position: {self._trekhaak.p}, angle: {self._trekhaak.M.angle}")
        
        return
    
    def getTrekhaakPosition(self):
        return self._trekhaak.p
    
        
    def getRaceCarPosition(self):
        return self._position.p