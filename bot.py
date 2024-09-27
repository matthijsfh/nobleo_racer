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
import copy

import json
import socket

from .caravan.caravan import caravan
from .racecar.racecar import racecar

DRAW_CARAVAN = True

# DEBUG = False
# DEBUG_TRACK = True
# DEBUG_CURVES= False
# DEBUG_CAR = False
# DEBUG_PLOT = True

DEBUG = False
DEBUG_TRACK = True
DEBUG_CURVES= False
DEBUG_CAR = False
DEBUG_PLOT = False


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
        
        self.max_velocity = 500.0
        self.min_velocity = 140.0
         
        if DRAW_CARAVAN:
            self._caravan = pygame.image.load(
                os.path.dirname(__file__) + '/caravan/caravan.png')
            
        self.firstPass = True    
        self.caravan = caravan("Kip", "De Lux", 1999)
        self.racecar = racecar()
        
        self.time = 0
        
        if (DEBUG_TRACK): 
            print(self.track.lines)
        
        #----------------------------------------------------------------------
        # Startup stuff. Calculate the track and vectors
        #----------------------------------------------------------------------
        # 47
        self.sectionCount = len(self.track.lines)

        # All coordinates including last one + list + next one.
        # Dus 2 langer dan sectionCount
        self.coordinates = [self.track.lines[-1]] + self.track.lines + [self.track.lines[0]]
        
        if (DEBUG_TRACK): 
            print(len(self.coordinates))

        # Dus 1 langer dan sectionCount
        self.relativeVectors = [c1 - c0 for c0, c1 in itertools.pairwise(self.coordinates)]

        # Calculate angles for each section
        self.absAngles = [math.degrees(math.atan2(y, x)) for x, y in self.relativeVectors]

        # Lenght of each section
        self.absLength = [math.sqrt(x**2 + y**2) for x, y in self.relativeVectors]
        
        if (DEBUG_TRACK):        
            for index, (vector, angle) in enumerate(zip(self.relativeVectors, self.absAngles)):
                print(f"Index: {index}, Vector: {vector}, Angle: {angle:.2f} deg")

        #----------------------------------------------------------------------
        # Label each section
        #----------------------------------------------------------------------
        self.rechtStuk = 100        # pixels rechtdoor

        # Ranking of each section
        self.curveType = ["None"] * self.sectionCount
        self.curveAngleChange= ["None"] * self.sectionCount
        
        for index in range(0, self.sectionCount):
            # Een lang stuk --> Recht
            if (self.absLength[index] >= self.rechtStuk):
                self.curveType[index] = "-"
                self.curveAngleChange[index] = 0
        
            else:
                tmp_angle = self.absAngles[index] - self.absAngles[index - 1]
                
                self.curveType[index] = "T"
                
                if (tmp_angle > 180):
                    tmp_angle = tmp_angle - 360
                
                self.curveAngleChange[index] = tmp_angle
                    

            if (DEBUG_TRACK):
                print(f"Index : {index} = {self.curveType[index]}, "
                      f"Angle : {self.curveAngleChange[index]:.0f}")                    

        
    def computeBrakeDistance(self, sectionIndex : int, counter : int):
        distance = (self.tmp_position - self.coordinates[(sectionIndex + 1) % self.sectionCount]).length()

        if (counter >= 2):
            distance = distance + (self.coordinates[(sectionIndex + 1) % self.sectionCount] - 
                                   self.coordinates[(sectionIndex + 2) % self.sectionCount]).length()

        if (counter >= 3):
            distance = distance + (self.coordinates[(sectionIndex + 2) % self.sectionCount] - 
                                   self.coordinates[(sectionIndex + 3) % self.sectionCount]).length()

        return distance
        
    
    def computeSectionVelocityAngles(self, sectionIndex):
        fullSpeed = 450;

        # From exel
        A = 0.00004
        B = 0.013
        x = abs(self.curveAngleChange[sectionIndex])

        _angleEffect = A * x**2 + B * x

        if (DEBUG_CURVES):
            print(f"Index : {sectionIndex}, curveAngleChange = {self.curveAngleChange[sectionIndex]:.1f}, angleEffect = {_angleEffect:.3f}")    

        result = fullSpeed * max((1 -_angleEffect), 150/fullSpeed)
        
        return result

    def compute_commands(self, next_waypoint: int, position: Transform, velocity: Vector2) -> Tuple:
        #----------------------------------------------------------------------
        # Set the racecar pose
        # Set the caravan pose
        #----------------------------------------------------------------------
        if (self.firstPass):
            self.firstPass = False;
       
        self.racecar.setPosition(position, DEBUG_CAR)
        self.racecar.calculateTrekhaak(DEBUG_CAR)
        self.racecar.updateOldPosition(position, DEBUG_CAR)

        self.time += 1.0/60
        self.absVelocity = velocity.length()

        self.distanceToTarget = abs((self.track.lines[next_waypoint] - position.p).length())

        #----------------------------------------------------------------------
        # Bochtje afsnijden
        #----------------------------------------------------------------------
        if (self.distanceToTarget < 50):
            next_waypoint = (next_waypoint + 1) % self.sectionCount
            
            if (DEBUG_CURVES):
                print("Bochtje afsnijden")

        #----------------------------------------------------------------------
        # target calculation
        #----------------------------------------------------------------------
        target = self.track.lines[next_waypoint]
        # calculate the target in the frame of the robot
        target = position.inverse() * target
        
        #----------------------------------------------------------------------
        # calculate the angle to the target
        #----------------------------------------------------------------------
        angle = target.as_polar()[1]
       
        self.tmp_position = Vector2(position.p)

        _sectionMaxVelocity   = self.computeSectionVelocityAngles(next_waypoint)
        
        # Brake zone 1
        _sectionExitVelocity1 = self.computeSectionVelocityAngles((next_waypoint + 1) % self.sectionCount)
        _sectionExitVelocity2 = self.computeSectionVelocityAngles((next_waypoint + 2) % self.sectionCount)
        _sectionExitVelocity3 = self.computeSectionVelocityAngles((next_waypoint + 3) % self.sectionCount)

        absDistToExit1 = self.computeBrakeDistance(next_waypoint, 1)
        absDistToExit2 = self.computeBrakeDistance(next_waypoint, 2)
        absDistToExit3 = self.computeBrakeDistance(next_waypoint, 3)

        allowed_velocity1 = _sectionExitVelocity1 + absDistToExit1 / 2.5    
        allowed_velocity2 = _sectionExitVelocity2 + absDistToExit2 / 2.5     
        allowed_velocity3 = _sectionExitVelocity3 + absDistToExit3 / 2.5  

        tmpTargetVelocity = min(min(min(allowed_velocity1, _sectionMaxVelocity), allowed_velocity2), allowed_velocity3)

        if velocity.length() < tmpTargetVelocity:
            throttle = 1
        else:
            throttle = -1
    
        if (DEBUG_TRACK):
            print(f"{next_waypoint}, "
                  f"Now : {self.curveType[next_waypoint]} ,"
                  f"Next : {self.curveType[(next_waypoint + 1) % self.sectionCount]} ,"
                  f"SectionMaxVelocity : {_sectionMaxVelocity:.0f}, "
                  f"Exit1 = {_sectionExitVelocity1:.0f}, "
                  f"Exit2 = {_sectionExitVelocity2:.0f}, "
                  f"Exit3 = {_sectionExitVelocity3:.0f}, "
                  f"Brakedist1 = {absDistToExit1:.0f}, "
                  f"Brakedist2 = {absDistToExit2:.0f}, "
                  f"Brakedist3 = {absDistToExit3:.0f}, "
                  f"TargetVelocity = {tmpTargetVelocity:.0f}" )
        #----------------------------------------------------------------------
        # calculate the steering
        #----------------------------------------------------------------------
        if angle > 0:
            steering = 1
        else:
            steering = -1
            
        #----------------------------------------------------------------------
        # Plotjuggler stuff        
        #----------------------------------------------------------------------
        if (DEBUG_PLOT):

            udp_ip = "127.0.0.1"  # replace with the actual IP address
            udp_port = 9870
            
            data = {}
            data["time"] = self.time
            data["next_waypoint"] = next_waypoint
            data["real_velocity"] = self.absVelocity
            data["target_velocity"] = tmpTargetVelocity
            data["distanceToTarget"] = self.distanceToTarget
            data["allowed_velocity1"] = allowed_velocity1
            data["allowed_velocity2"] = allowed_velocity2
            data["allowed_velocity3"] = allowed_velocity3
            
            json_data = json.dumps(data)
            
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Send JSON data
            sock.sendto(json_data.encode('utf-8'), (udp_ip, udp_port))
            sock.close()
        
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
