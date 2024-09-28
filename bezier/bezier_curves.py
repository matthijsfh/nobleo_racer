# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 23:18:35 2024

@author: matth
"""

import numpy as np
import matplotlib.pyplot as plt

# Function to compute a point on a quadratic Bézier curve
def quadratic_bezier(t, P0, P1, P2):
    return (1 - t)**2 * P0 + 2 * (1 - t) * t * P1 + t**2 * P2

# Control points
P0 = np.array([0, 0])    # Starting point
P1 = np.array([1, 2])    # Control point
P2 = np.array([3, 0])    # End point

# Generate points along the curve
t_values = np.linspace(0, 1, 3)
curve_points = [quadratic_bezier(t, P0, P1, P2) for t in t_values]
curve_points = np.array(curve_points)

# Plot the Bézier curve
plt.plot(curve_points[:, 0], curve_points[:, 1], label='Bézier Curve')

# Plot control points
plt.plot([P0[0], P1[0], P2[0]], [P0[1], P1[1], P2[1]], 'ro--', label='Control Points')

# Add labels and legend
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.title('Quadratic Bézier Curve')
plt.grid(True)
plt.show()

