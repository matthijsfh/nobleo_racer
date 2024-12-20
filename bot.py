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
import numpy as np

from .caravan.caravan import caravan
from .racecar.racecar import racecar


# Kwadratic = 1.2
# Linear = 13
# fullSpeed = 530


Kwadratic = 1.423694140452873
Linear = 12.749
fullSpeed = 528.6129

# Params = [QuadraticGainA: 1.423694140452873, LinearGainB: 12.749571770183502, fullSpeed: 528.6129919969993]

DRAW_CARAVAN = True
DEBUG = False
DEBUG_TRACK = False
DEBUG_CURVES = False
DEBUG_CAR = False
DEBUG_PLOT = False
DEBUG_TRACK_PLOT = False
BOCHT_AFSNIJDEN = False

# DEBUG = False
# DEBUG_TRACK = False
# DEBUG_CURVES= False
# DEBUG_CAR = False
# DEBUG_PLOT = False
# DEBUG_TRACK_PLOT = False
# BOCHT_AFSNIJDEN = False


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

    def bezier_curve(self, p0, p1, p2, num_points=10):
        """Generates a quadratic Bezier curve given 3 control points."""
        t = np.linspace(0, 1, num_points).reshape(-1, 1)  # Reshape to column vector
        curve = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t**2 * p2
        return curve

    def bochtenAfsnijden(self):
        for i in range(0, self.sectionCount):
            # for i in range(0, 1):

            # print(track_lines[i])
            print(self.relativeVectors[i])

            lengte1 = self.relativeVectors[(i - 0) % self.sectionCount].length()
            lengte2 = self.relativeVectors[(i + 1) % self.sectionCount].length()

            print(lengte1)
            print(lengte2)

            magic = 50

            # Calculate new point on the line close to the exit
            newPoint1 = Vector2(
                self.relativeVectors[(i - 0) % self.sectionCount] * (1 - magic / lengte1)
                + self.track.lines[(i - 1) % (self.sectionCount)]
            )
            newPoint2 = Vector2(
                self.relativeVectors[(i + 1) % self.sectionCount] * (magic / lengte2)
                + self.track.lines[i]
            )

            self.curve = self.bezier_curve(newPoint1, self.track.lines[i], newPoint2, 3)

            tmp = Vector2(self.curve[1][0], self.curve[1][1])

            self.myNewCoordinates[i] = Vector2(tmp)

        return

    def bochtenAfsnijden_v2(self):
        scherpebocht = False

        for i in range(0, self.sectionCount):
            # print (self.relativeVectors[i])

            lengte1 = self.relativeVectors[(i - 0) % self.sectionCount].length()
            lengte2 = self.relativeVectors[(i + 1) % self.sectionCount].length()

            # print (lengte1)
            # print (lengte2)

            # relAngle1 = abs(self.absAngles[(i-1) % self.sectionCount] - self.absAngles[(i+0) % self.sectionCount])
            # relAngle2 = abs(self.absAngles[(i+0) % self.sectionCount] - self.absAngles[(i+1) % self.sectionCount])
            # relAngle3 = abs(self.absAngles[(i+1) % self.sectionCount] - self.absAngles[(i+2) % self.sectionCount])

            relAngle1 = abs(
                self.absAngles[(i + 0) % self.sectionCount]
                - self.absAngles[(i + 1) % self.sectionCount]
            )
            relAngle2 = abs(
                self.absAngles[(i + 1) % self.sectionCount]
                - self.absAngles[(i + 2) % self.sectionCount]
            )
            relAngle3 = abs(
                self.absAngles[(i + 2) % self.sectionCount]
                - self.absAngles[(i + 3) % self.sectionCount]
            )

            if relAngle1 > 180:
                relAngle1 = 360 - relAngle1

            if relAngle2 > 180:
                relAngle2 = 360 - relAngle2

            if relAngle3 > 180:
                relAngle3 = 360 - relAngle3

            print(
                f"section = {i}, angle1 = {relAngle1:.1f}, angle2 = {relAngle2:.1f}, angle3 = {relAngle3:.1f}"
            )

            # lange bocht
            if (relAngle1 > 30) and (relAngle2 > 30) and (relAngle3 > 30):
                magic = -50
                scherpebocht = True

            elif (relAngle1 > 20) and (relAngle2 > 20) and (relAngle3 > 20):
                magic = -40
                scherpebocht = True

            # elif (relAngle1 > 20) and (relAngle2 > 20) and (relAngle3 < 20):
            #     magic = 30
            #     scherpebocht = False

            elif scherpebocht:
                magic = 30

            else:
                magic = 0

            # Calculate new point on the line close to the exit
            newPoint1 = Vector2(
                self.relativeVectors[(i - 0) % self.sectionCount] * (1 - magic / lengte1)
                + self.track.lines[(i - 1) % (self.sectionCount)]
            )
            newPoint2 = Vector2(
                self.relativeVectors[(i + 1) % self.sectionCount] * (magic / lengte2)
                + self.track.lines[i]
            )

            self.curve = self.bezier_curve(newPoint1, self.track.lines[i], newPoint2, 3)

            tmp = Vector2(self.curve[1][0], self.curve[1][1])

            self.myNewCoordinates[i] = Vector2(tmp)
        return

    def __init__(self, track):
        super().__init__(track)
        self.color = (0xFF, 0x80, 0)
        self._last_position = 0

        self._black = pygame.Color(0, 0, 0, 50)
        self._green = pygame.Color(0, 255, 0, 50)
        self._red = pygame.Color(255, 0, 0, 50)
        self._blue = pygame.Color(0, 0, 255, 50)

        self.max_velocity = 500.0
        self.min_velocity = 140.0

        if DRAW_CARAVAN:
            self._caravan = pygame.image.load(os.path.dirname(__file__) + "/caravan/caravan.png")

        self.firstPass = True
        self.firstDraw = True

        self.caravan = caravan("Kip", "De Luxe", 1999)
        self.racecar = racecar()

        self.time = 0
        self.angle = 0

        # self.postionCarOld = Transform(None, [0,0])
        self.postionCarOld = Vector2([0, 0])
        self.postionCar = Vector2([0, 0])

        # ----------------------------------------------------------------------
        # Orginele baan (track 1 = 47)
        # Orginele baan (track 2 = 49)
        # ----------------------------------------------------------------------
        self.sectionCount = len(self.track.lines)

        # ----------------------------------------------------------------------
        # Nasty hack
        # ----------------------------------------------------------------------
        self.trackNo = 0

        if (self.sectionCount >= 45) and (self.sectionCount <= 48):
            self.trackNo = 1

            i = 43 - 1
            self.track.lines[i][0] = self.track.lines[i][0] + 15
            self.track.lines[i][1] = self.track.lines[i][1]

            i = 44 - 1
            self.track.lines[i][0] = self.track.lines[i][0] + 15
            self.track.lines[i][1] = self.track.lines[i][1]

        if (self.sectionCount >= 49) and (self.sectionCount <= 51):
            self.trackNo = 2

            i = 35 - 1
            self.track.lines[i][1] = self.track.lines[i][1] - 10

            i = 36 - 1
            self.track.lines[i][0] = self.track.lines[i][0] - 10
            self.track.lines[i][1] = self.track.lines[i][1] - 10

            i = 43 - 1
            self.track.lines[i][1] = self.track.lines[i][1] - 10


        if (self.sectionCount >= 65) and (self.sectionCount <= 70):
            self.trackNo = 3

            i = 13
            self.track.lines[i][0] = self.track.lines[i][0] - 10

        # ----------------------------------------------------------------------
        # All coordinates including last one + list + next one.
        # Dus 2 langer dan sectionCount
        # ----------------------------------------------------------------------
        self.coordinates = [self.track.lines[-1]] + self.track.lines + [self.track.lines[0]]

        # Dus 1 langer dan sectionCount
        self.relativeVectors = [c1 - c0 for c0, c1 in itertools.pairwise(self.coordinates)]

        # Calculate angles for each section
        self.absAngles = [math.degrees(math.atan2(y, x)) for x, y in self.relativeVectors]

        # Lenght of each section
        self.absLength = [math.sqrt(x**2 + y**2) for x, y in self.relativeVectors]

        if DEBUG_TRACK:
            for index, (vector, angle) in enumerate(zip(self.relativeVectors, self.absAngles)):
                print(f"Index: {index}, Vector: {vector}, Angle: {angle:.2f} deg")

        # ----------------------------------------------------------------------
        # Bochtjes afsnijden met nieuwe curve.
        # Werkt niet lekke.
        # Bochten worden er krapper van. Dat werkt niet lekker.
        # ----------------------------------------------------------------------
        self.myNewCoordinates = [self.coordinates[i] for i in range(len(self.coordinates))]

        # if (BOCHT_AFSNIJDEN):

        #     self.bochtenAfsnijden_v2()

        #     if (DEBUG_TRACK):
        #         print('----------------------------------------')
        #         print(len(self.coordinates))
        #         print(self.coordinates)
        #         print('----------------------------------------')
        #         print(len(self.myNewCoordinates))
        #         print(self.myNewCoordinates)
        #         print('----------------------------------------')

        #     # Met nieuwe punten, alles herberekenen
        #     self.coordinates = [self.myNewCoordinates[i] for i in range(len(self.myNewCoordinates))]

        #     # Opnieuw
        #     # Dus 1 langer dan sectionCount
        #     self.relativeVectors = [c1 - c0 for c0, c1 in itertools.pairwise(self.coordinates)]

        #     # Calculate angles for each section
        #     self.absAngles = [math.degrees(math.atan2(y, x)) for x, y in self.relativeVectors]

        #     # Lenght of each section
        #     self.absLength = [math.sqrt(x**2 + y**2) for x, y in self.relativeVectors]

        # ----------------------------------------------------------------------
        # Debug
        # ----------------------------------------------------------------------
        if DEBUG_TRACK:
            for index, (vector, angle) in enumerate(zip(self.relativeVectors, self.absAngles)):
                print(f"Index: {index}, Vector: {vector}, Angle: {angle:.2f} deg")

        if DEBUG_TRACK:
            print(len(self.coordinates))

        # ----------------------------------------------------------------------
        # Label each section
        # ----------------------------------------------------------------------
        self.rechtStuk = 100  # pixels rechtdoor

        # Ranking of each section
        self.curveType = ["None"] * self.sectionCount
        self.curveAngleChange = ["None"] * self.sectionCount

        for index in range(0, self.sectionCount):
            # Een lang stuk --> Recht
            if self.absLength[index] >= self.rechtStuk:
                self.curveType[index] = "-"
                self.curveAngleChange[index] = 0

            else:
                relAngle = self.absAngles[index] - self.absAngles[index - 1]

                self.curveType[index] = "T"

                if relAngle > 180:
                    relAngle = 360 - relAngle

                self.curveAngleChange[index] = relAngle

            if DEBUG_TRACK:
                print(
                    f"Index : {index} = {self.curveType[index]}, "
                    f"Angle : {self.curveAngleChange[index]:.0f}"
                )

    def computeBrakeDistance(self, sectionIndex: int, counter: int):
        distance = (
            self.tmp_position - self.coordinates[(sectionIndex + 1) % self.sectionCount]
        ).length()

        if counter >= 2:
            distance = (
                distance
                + (
                    self.coordinates[(sectionIndex + 1) % self.sectionCount]
                    - self.coordinates[(sectionIndex + 2) % self.sectionCount]
                ).length()
            )

        if counter >= 3:
            distance = (
                distance
                + (
                    self.coordinates[(sectionIndex + 2) % self.sectionCount]
                    - self.coordinates[(sectionIndex + 3) % self.sectionCount]
                ).length()
            )

        return distance

    def computeSectionVelocityAngles(self, sectionIndex):
        # From exel
        # A = 0.00004
        # B = 0.013

        # fullSpeed = 530
        # A = 1.2 / 10000
        # B = 13 / 1000

        A = Kwadratic / 10000
        B = Linear / 1000

        x = abs(self.curveAngleChange[sectionIndex])

        _angleEffect = A * x**2 + B * x

        if DEBUG_CURVES:
            print(
                f"Index : {sectionIndex}, curveAngleChange = {self.curveAngleChange[sectionIndex]:.1f}, angleEffect = {_angleEffect:.3f}"
            )

        # Soort van minimum speed door de bochten
        # result = fullSpeed * max((1 -_angleEffect), 150/fullSpeed)
        # 170 is max track 2.
        # 160 is max track 1. Maar met verschoven bocht is 170 ook goed.
        # 150 = Safe default voor track 3.

        if self.trackNo >= 1:
            result = fullSpeed * max((1 - _angleEffect), 170 / fullSpeed)
        else:
            result = fullSpeed * max((1 - _angleEffect), 150 / fullSpeed)

        return result

    def compute_commands(self, next_waypoint: int, position: Transform, velocity: Vector2) -> Tuple:
        # ----------------------------------------------------------------------
        # Set the racecar pose
        # Set the caravan pose
        # ----------------------------------------------------------------------
        self.racecar.setPosition(position, DEBUG_CAR)
        self.racecar.calculateTrekhaak(DEBUG_CAR)
        self.racecar.updateOldPosition(position, DEBUG_CAR)

        self.time += 1.0 / 60
        self.absVelocity = velocity.length()

        # Orgninele code
        self.distanceToTarget = abs((self.track.lines[next_waypoint] - position.p).length())

        # ----------------------------------------------------------------------
        # Vreemde code die veel doet.
        # Trekt de auto recht door gauw naar het volgende punt te kijken.
        # Doet bij track 1 wel iets.
        # Doet bij track 2 veel met al die korte bochten.
        # 60 werkt overal.
        # ----------------------------------------------------------------------
        if self.distanceToTarget < 60:
            next_waypoint = (next_waypoint + 1) % self.sectionCount

        # ----------------------------------------------------------------------
        # Extra de bocht doorkijken werkt bij track 1, maar bij 2 vliegt auto uit de bocht.
        # ----------------------------------------------------------------------
        if self.trackNo == 1:
            if (self.distanceToTarget >= 60) and (self.distanceToTarget < 70):
                next_waypoint = (next_waypoint + 1) % self.sectionCount

        # ----------------------------------------------------------------------
        # Niet meer nodig na aanpassen punten in circuit.
        # ----------------------------------------------------------------------
        # if self.trackNo == 2:
        #     # Nodig voor track 2.
        #     if next_waypoint == 36:
        #         next_waypoint = 37

        # ----------------------------------------------------------------------
        # target calculation
        # ----------------------------------------------------------------------
        target = self.track.lines[next_waypoint]

        # calculate the target in the frame of the robot
        target = position.inverse() * target

        # ----------------------------------------------------------------------
        # calculate the angle to the target
        # ----------------------------------------------------------------------
        self.angle = target.as_polar()[1]

        # ----------------------------------------------------------------------
        # Differentiate
        # ----------------------------------------------------------------------
        self.absCarAngle = position.M.angle
        self.absCarMoveAngle = 0

        self.postionCarOld = self.postionCar
        self.postionCar = Vector2(position.p)

        tmp = Vector2(self.postionCar - self.postionCarOld)

        self.absCarMoveAngle = math.atan2(tmp[1], tmp[0])
        self.slipAngle = self.absCarAngle - self.absCarMoveAngle

        if self.firstPass:
            self.firstPass = False
            self.slipAngle = 0

        self.slipAngleDeg = self.slipAngle / math.pi * 180

        if self.slipAngleDeg >= 180:
            self.slipAngleDeg -= 360

        if self.slipAngleDeg <= -180:
            self.slipAngleDeg += 360

        # ----------------------------------------------------------------------
        # Braking and some magic
        # ----------------------------------------------------------------------
        self.tmp_position = Vector2(position.p)

        _sectionMaxVelocity = self.computeSectionVelocityAngles(next_waypoint)

        # Brake zone 1
        _sectionExitVelocity1 = self.computeSectionVelocityAngles(
            (next_waypoint + 1) % self.sectionCount
        )
        _sectionExitVelocity2 = self.computeSectionVelocityAngles(
            (next_waypoint + 2) % self.sectionCount
        )
        _sectionExitVelocity3 = self.computeSectionVelocityAngles(
            (next_waypoint + 3) % self.sectionCount
        )

        absDistToExit1 = self.computeBrakeDistance(next_waypoint, 1)
        absDistToExit2 = self.computeBrakeDistance(next_waypoint, 2)
        absDistToExit3 = self.computeBrakeDistance(next_waypoint, 3)

        allowed_velocity1 = _sectionExitVelocity1 + absDistToExit1 / 2.5
        allowed_velocity2 = _sectionExitVelocity2 + absDistToExit2 / 2.5
        allowed_velocity3 = _sectionExitVelocity3 + absDistToExit3 / 2.5

        # Die _sectionMaxVelocity voorkomt dat de auto uit de bocht vliegt bij de het laatste segment.
        # Geen idee waarom
        tmpTargetVelocity = min(
            min(min(allowed_velocity1, _sectionMaxVelocity), allowed_velocity2),
            allowed_velocity3,
        )

        if DEBUG_TRACK:
            print(
                f"{next_waypoint}, "
                f"Now : {self.curveType[next_waypoint]} ,"
                f"Next : {self.curveType[(next_waypoint + 1) % self.sectionCount]} ,"
                f"SectionMaxVelocity : {_sectionMaxVelocity:.0f}, "
                f"Exit1 = {_sectionExitVelocity1:.0f}, "
                f"Exit2 = {_sectionExitVelocity2:.0f}, "
                f"Exit3 = {_sectionExitVelocity3:.0f}, "
                f"Brakedist1 = {absDistToExit1:.0f}, "
                f"Brakedist2 = {absDistToExit2:.0f}, "
                f"Brakedist3 = {absDistToExit3:.0f}, "
                f"TargetVelocity = {tmpTargetVelocity:.0f}"
            )

        # ----------------------------------------------------------------------
        # calculate the throttle
        # ----------------------------------------------------------------------
        if velocity.length() < tmpTargetVelocity:
            throttle = 1
        else:
            throttle = -1

        # ----------------------------------------------------------------------
        # calculate the steering
        # ----------------------------------------------------------------------
        # if angle > 0:
        #     steering = 1
        # else:
        #     steering = -1

        # if self.angle > 2:
        #     steering = 1
        # elif self.angle < -2:
        #     steering = -1
        # else:
        #     steering = 0

        # Gepikt
        steering = self.angle / 3

        # ----------------------------------------------------------------------
        # Doet niet wat ik wil
        # ----------------------------------------------------------------------
        # if (abs(self.slipAngleDeg) > 20):
        #     throttle = 0

        # ----------------------------------------------------------------------
        # Debug logging
        # ----------------------------------------------------------------------
        if DEBUG_TRACK:
            print(
                f"{next_waypoint}, "
                f"Now : {self.curveType[next_waypoint]} ,"
                f"Next : {self.curveType[(next_waypoint + 1) % self.sectionCount]} ,"
                f"SectionMaxVelocity : {_sectionMaxVelocity:.0f}, "
                f"Exit1 = {_sectionExitVelocity1:.0f}, "
                f"Exit2 = {_sectionExitVelocity2:.0f}, "
                f"Exit3 = {_sectionExitVelocity3:.0f}, "
                f"Brakedist1 = {absDistToExit1:.0f}, "
                f"Brakedist2 = {absDistToExit2:.0f}, "
                f"Brakedist3 = {absDistToExit3:.0f}, "
                f"TargetVelocity = {tmpTargetVelocity:.0f}, "
                f"throttle = {throttle:.0f}, "
                f"steering = {steering:.0f}, "
            )

        # ----------------------------------------------------------------------
        # Plotjuggler stuff
        # ----------------------------------------------------------------------
        if DEBUG_PLOT:
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
            data["throttle"] = throttle
            data["steering"] = steering
            data["absCarAngle"] = self.absCarAngle / math.pi * 180
            data["absCarMoveAngle"] = self.absCarMoveAngle / math.pi * 180
            data["slipAngle"] = self.slipAngleDeg

            json_data = json.dumps(data)

            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Send JSON data
            sock.sendto(json_data.encode("utf-8"), (udp_ip, udp_port))
            sock.close()

        return throttle, steering

    # ----------------------------------------------------------------------
    # Draw
    # ----------------------------------------------------------------------
    def draw(self, map_scaled, zoom):
        if DEBUG_TRACK_PLOT:
            for i in range(0, self.sectionCount):
                pygame.draw.line(
                    map_scaled,
                    self._green,
                    self.myNewCoordinates[i] * zoom,
                    self.myNewCoordinates[i + 1] * zoom,
                    2,
                )

                pygame.draw.line(
                    map_scaled,
                    self._blue,
                    self.coordinates[i] * zoom,
                    self.coordinates[i + 1] * zoom,
                    2,
                )

        if DRAW_CARAVAN:
            # Plot the trekhaak lijn voor debugging
            _tmpTrekhaak = self.racecar.getTrekhaakPosition()
            _tmpRacecar = self.racecar.getRaceCarPosition()
            _tmpCaravanVector = self.racecar.getRaceCarOldPosition()

            tmp = Vector2(_tmpTrekhaak - _tmpCaravanVector)
            _tmpCaravanAngle = math.atan2(tmp.y, tmp.x) / math.pi * 180

            if DEBUG:
                print(f"Caravan abs angle : {_tmpCaravanAngle}")

                pygame.draw.line(
                    map_scaled,
                    self._green,
                    _tmpTrekhaak * zoom,
                    _tmpRacecar * zoom,
                    2,
                )

                pygame.draw.line(
                    map_scaled,
                    self._red,
                    _tmpTrekhaak * zoom,
                    _tmpCaravanVector * zoom,
                    2,
                )

            # Plot the caravan.
            caravanZoom = 0.4 * zoom
            caravan_image = pygame.transform.rotozoom(self._caravan, -_tmpCaravanAngle, caravanZoom)

            angle = Transform(
                _tmpCaravanAngle / 180 * math.pi,
                [_tmpTrekhaak[0], _tmpTrekhaak[1]],
            )

            caravan_rect = caravan_image.get_rect(center=(angle.p + angle.M * Vector2(0, 0)) * zoom)
            map_scaled.blit(caravan_image, caravan_rect)

        return
