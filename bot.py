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
DRAW_FLAME = False

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
        self.color = (255, 255, 0)
        self._last_position = 0
        
        
        if DEBUG:
            self._font = pygame.font.SysFont(None, 24)
            self._black = pygame.Color(0, 0, 0, 50)
            self._green = pygame.Color(0, 255, 0, 50)
            self._red = pygame.Color(255, 0, 0, 50)
         
        if DRAW_FLAME:
            self._flame = pygame.image.load(
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
        
        # print(type(position))
        print(position.M.angle)
        
        #----------------------------------------------------------------------
        # Set the racecar pose
        # Set the caravan pose
        #----------------------------------------------------------------------
        if (self.firstPass):
            self.firstPass = False;
            
            # self.racecar.setPosition(position)
            # self.racecar.calculateTrekhaak()
       
        self.racecar.setPosition(position)
        self.racecar.calculateTrekhaak()


        target = self.track.lines[next_waypoint]

        # print (target)
        # calculate the target in the frame of the robot
        target = position.inverse() * target


        #----------------------------------------------------------------------
        # Update the caravan
        #----------------------------------------------------------------------
        # self.caravan.updateCarPosition(position)

        
        
        
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

    
        # Accelerate when long straight
        
        # Calc brake distance
        
        # Accelerate when leaving corner


        if DRAW_FLAME:
            self._last_position = position

        #----------------------------------------------------------------------
        # calculate the steering
        #----------------------------------------------------------------------
        if angle > 0:
            steering = 1
        else:
            steering = -1
        
        return throttle, steering

    def draw(self, map_scaled, zoom):

        if DRAW_FLAME:
            flame_pos = self._last_position
            flame_zoom = 0.4 * zoom
            flame_angle = flame_pos.M.angle
            flame_image = pygame.transform.rotozoom(
                self._flame, -math.degrees(flame_angle), flame_zoom)
                # self._flame, -math.degrees(flame_angle) - 45, flame_zoom)
            flame_rect = flame_image.get_rect(
                center=(flame_pos.p - flame_pos.M * Vector2(40, 0)) * zoom)
            map_scaled.blit(flame_image, flame_rect)
        
        
        # Plot the trekhaak lijn voor debugging
        tmp_trekhaak = self.racecar.getTrekhaakPosition()
        tmp_racecar = self.racecar.getRaceCarPosition()
        
        print((tmp_racecar))
        print((tmp_trekhaak))
    
        # pygame.draw.line(map_scaled, self._green,
        #                   Vector2(100,1) * zoom,
        #                   Vector2(0, 0)  * zoom, 2) 

        pygame.draw.line(map_scaled, self._green,
                          tmp_trekhaak * zoom,
                          tmp_racecar  * zoom, 2) 
        
        
        # pygame.draw.line(map_scaled, self._green,
        #                  self._last_coordinates * zoom,
        #                  self._coordinates[self._last_steer_wp] * zoom, 2)
        
        # time.sleep(1)
        
        return
