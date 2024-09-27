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
    Vector2(650.14, 395.908), Vector2(716.11, 429.371), Vector2(828.928, 444.669), Vector2(1389.2, 440.844)
]

def plotVectors():
    # Extract X and Y coordinates
    x_vals = [v[0] for v in track_lines]
    y_vals = [-1*v[1] for v in track_lines]
    
    # Plot the vectors
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, marker='o')
    plt.title('XY Graph of Vectors')
    plt.xlabel('X Coordinates')
    plt.ylabel('Y Coordinates')
    plt.grid(True)
    plt.show()
    
    return

# def bezier_curve(p0, p1, p2, p3, num_points=100):
#     """Generates a cubic Bezier curve given 4 control points."""
#     t = np.linspace(0, 1, num_points).reshape(-1, 1)  # Reshape to column vector
#     curve = (1-t)**3 * p0 + 3*(1-t)**2 * t * p1 + 3*(1-t) * t**2 * p2 + t**3 * p3
#     return curve


def bezier_curve(p0, p1, p2, num_points=100):
    """Generates a quadratic Bezier curve given 3 control points."""
    t = np.linspace(0, 1, num_points).reshape(-1, 1)  # Reshape to column vector
    curve = (1-t)**2 * p0 + 2*(1-t) * t * p1 + t**2 * p2
    return curve

# Bezier smoothing function
def smooth_track(track_lines, num_points_per_segment = 10):
    smoothed_points = []
    
    for i in range(0, len(track_lines) - 2, 2):
        p0 = np.array([track_lines[i].x, track_lines[i].y])
        p1 = np.array([track_lines[i + 1].x, track_lines[i + 1].y])
        p2 = np.array([track_lines[i + 2].x, track_lines[i + 2].y])
        # p3 = np.array([track_lines[i + 3].x, track_lines[i + 3].y])
        
        # Generate Bezier curve points for this segment
        # bezier_points = bezier_curve(p0, p1, p2, p3, num_points=num_points_per_segment)
        bezier_points = bezier_curve(p0, p1, p2, num_points=num_points_per_segment)
        smoothed_points.extend(bezier_points)
    
    return np.array(smoothed_points)

def main():
    coordinates = [track_lines[-1]] + track_lines + [track_lines[0]]
    relativeVectors = [c1 - c0 for c0, c1 in itertools.pairwise(coordinates)]
    absAngles = [math.degrees(math.atan2(y, x)) for x, y in relativeVectors]    
    absLength = [math.sqrt(x**2 + y**2) for x, y in relativeVectors]

    # Smooth the track using Bezier curves
    smoothed_points = smooth_track(track_lines)

    # Plot the original points and the smoothed curve
    plt.figure(figsize=(10, 6))
    plt.plot([v.x for v in track_lines], [v.y for v in track_lines], 'o--', label="Original Track")
    plt.plot(smoothed_points[:, 0], smoothed_points[:, 1], '*', label="Smoothed Track", color="red")
    plt.title("Bezier Curve Smoothing")
    plt.xlabel("X Coordinates")
    plt.ylabel("Y Coordinates")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    main()

