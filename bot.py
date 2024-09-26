from typing import Tuple
from pygame import Vector2
from ...bot import Bot
from ...linear_math import Transform
import os
from pygame import Vector2
import pygame
import math
import itertools
import time

from .caravan.caravan import caravan
from .racecar.racecar import racecar

DEBUG = True
# DEBUG = False
DRAW_CARAVAN = True

class MatthijsRacer(Bot):
    @property
    def name(self):
        return "CaravanRacer"

    @property
    def contributor(self):
        return "Matthijs"
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        self._color = value
    
    def __init__(self, track):
        super().__init__(track)
        self.color = (0xff, 0x80, 0)
        self._last_position = 0
        
        self._black = pygame.Color(0, 0, 0, 50)
        self._green = pygame.Color(0, 255, 0, 50)
        self._red = pygame.Color(255, 0, 0, 50)
         
        if DRAW_CARAVAN:
            self._caravan = pygame.image.load(
                os.path.dirname(__file__) + '/caravan/caravan.png')
            
        self.firstPass = True    
        self.caravan = caravan("Kip", "De Lux", 1999)
        self.racecar = racecar()
        
        #----------------------------------------------------------------------
        # Startup stuff. Calculate the track and vectors
        #----------------------------------------------------------------------
        # All coordinates including last one + list + next one.
        self.coordinates = [self.track.lines[-1]] + self.track.lines + [self.track.lines[0]]
        self.relativeVectors = [c1 - c0 for c0, c1 in itertools.pairwise(self.coordinates)]
        
        # Calculate angles for each vector
        self.absAngles = [math.degrees(math.atan2(y, x)) for x, y in self.relativeVectors]

        if (DEBUG):        
            for vector, angle in zip(self.relativeVectors, self.absAngles):
                print(f"Vector: {vector}, Angle: {angle:.2f} deg")
        

    def compute_commands(self, next_waypoint: int, position: Transform, velocity: Vector2) -> Tuple:
        #----------------------------------------------------------------------
        # Set the racecar pose
        # Set the caravan pose
        #----------------------------------------------------------------------
        if (self.firstPass):
            self.firstPass = False;
            
            # self.racecar.setPosition(position)
            # self.racecar.calculateTrekhaak()
       
        self.racecar.setPosition(position, DEBUG)
        self.racecar.calculateTrekhaak(DEBUG)

        self.racecar.updateOldPosition(position, DEBUG)


        target = self.track.lines[next_waypoint]

        # print (target)
        # calculate the target in the frame of the robot
        target = position.inverse() * target

        
        #----------------------------------------------------------------------
        # calculate the angle to the target
        #----------------------------------------------------------------------
        angle = target.as_polar()[1]
        

        #----------------------------------------------------------------------
        # calculate the throttle
        #----------------------------------------------------------------------
        target_velocity = 100
        if velocity.length() < target_velocity:
            throttle = 1
        else:
            throttle = -1

    
        #----------------------------------------------------------------------
        # Accelerate when long straight
        # Calc brake distance
        # Accelerate when leaving corner
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        # calculate the steering
        #----------------------------------------------------------------------
        if angle > 0:
            steering = 1
        else:
            steering = -1
        
        return throttle, steering


    #----------------------------------------------------------------------
    # Draw 
    #----------------------------------------------------------------------
    def draw(self, map_scaled, zoom):
        
        if DRAW_CARAVAN:
        
            # Plot the trekhaak lijn voor debugging
            _tmpTrekhaak = self.racecar.getTrekhaakPosition()
            _tmpRacecar = self.racecar.getRaceCarPosition()
            _tmpCaravanVector = self.racecar.getRaceCarOldPosition()
            
            tmp = Vector2(_tmpTrekhaak- _tmpCaravanVector)
            _tmpCaravanAngle = math.atan2(tmp.y, tmp.x) / math.pi * 180
            
            if (DEBUG):
                print(f"Caravan abs angle : {_tmpCaravanAngle}")

                pygame.draw.line(map_scaled, self._green,
                                  _tmpTrekhaak * zoom,
                                  _tmpRacecar  * zoom, 2) 
        
                pygame.draw.line(map_scaled, self._red,
                                  _tmpTrekhaak * zoom,
                                  _tmpCaravanVector  * zoom, 2) 
        
            # Plot the caravan.        
            caravanZoom = 0.4 * zoom
            caravan_image = pygame.transform.rotozoom(self._caravan, -_tmpCaravanAngle, caravanZoom)
            
            angle = Transform(_tmpCaravanAngle /180 * math.pi, [_tmpTrekhaak[0], _tmpTrekhaak[1]])

            caravan_rect = caravan_image.get_rect(center=(angle.p + angle.M * Vector2(0, 0)) * zoom)
            map_scaled.blit(caravan_image, caravan_rect)
        
        return
