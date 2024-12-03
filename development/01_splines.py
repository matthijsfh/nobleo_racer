# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 17:07:02 2024

@author: matth
"""

import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt

# Example data (2D)
x = np.linspace(0, 10, 10)
y = np.sin(x)

# Fit a spline to the data
tck, u = interpolate.splprep([x, y], s=0)

# Generate new points along the spline
unew = np.linspace(0, 1, 100)
out = interpolate.splev(unew, tck)

# Plot
plt.plot(x, y, 'o', label='Data points')
plt.plot(out[0], out[1], label='Interpolated Spline')
plt.legend()
plt.show()
