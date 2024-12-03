import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt

import addcopyfighandler

# Assuming you have a Vector2 class like this
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# track_lines = [ Vector2(1389.2, 440.844) ,  Vector2(1466.64, 452.317) ,  Vector2(1518.27, 497.253) , 
#                 Vector2(1524, 556.531) ,  Vector2(1487.67, 628.237) ,  Vector2(1375.81, 692.295) , 
#                 Vector2(1235.27, 743.924) ,  Vector2(800.246, 854.83) ,  Vector2(405.381, 919.844) ,
#                 Vector2(262.924, 894.03) ,  Vector2(205.559, 829.972) ,  Vector2(211.295, 782.168) , 
#                 Vector2(272.485, 764.002) ,  Vector2(620.501, 769.738) ,  Vector2(802.158, 742.968) , 
#                 Vector2(848.05, 711.417) ,  Vector2(872.908, 643.535) ,  Vector2(865.26, 575.653) , 
#                 Vector2(820.324, 528.804) ,  Vector2(775.387, 509.683) ,  Vector2(159.667, 445.625) , 
#                 Vector2(97.521, 406.425) ,  Vector2(71.7066, 336.631) ,  Vector2(87.004, 276.397) , 
#                 Vector2(132.896, 232.417) ,  Vector2(210.339, 219.032) ,  Vector2(482.824, 243.89) ,
#                 Vector2(566.96, 227.637) ,  Vector2(768.695, 89.0038) ,  Vector2(833.709, 75.6186) , 
#                 Vector2(925.493, 88.0477) ,  Vector2(1219.97, 193.217) ,  Vector2(1373.9, 220.944) , 
#                 Vector2(1419.79, 205.647) ,  Vector2(1562.25, 117.686) ,  Vector2(1642.56, 97.6086) , 
#                 Vector2(1746.77, 111.95) ,  Vector2(1818.48, 174.096) ,  Vector2(1829.95, 240.066) , 
#                 Vector2(1792.67, 275.441) ,  Vector2(1681.76, 283.09) ,  Vector2(760.09, 281.177) , 
#                 Vector2(678.823, 309.86) ,  Vector2(640.579, 351.928) ,  Vector2(650.14, 395.908) , 
#                 Vector2(716.11, 429.371) ,  Vector2(828.928, 444.669), Vector2(1389.2, 440.844), 
#                 Vector2(1466.64, 452.317) ]

track_lines = [Vector2(1226.28, 739.132) ,  Vector2(985.756, 907.34) ,  Vector2(964.774, 953.116) ,  
               Vector2(985.038, 996.355) ,  Vector2(1035.95, 1024.54) ,  Vector2(1316.56, 1101.56) ,  
               Vector2(1365.82, 1178.76) ,  Vector2(1345.74, 1246.82) ,  Vector2(1296.9, 1263.92) ,  
               Vector2(999.613, 1239.62) ,  Vector2(888.739, 1145.31) ,  Vector2(846.91, 1135.62) ,  
               Vector2(806.472, 1147.37) ,  Vector2(765.973, 1227.95) ,  Vector2(652.502, 1253.92) ,  
               Vector2(533.158, 1230.68) ,  Vector2(409.141, 1138.79) ,  Vector2(316.975, 1017.87) ,  
               Vector2(276.696, 929.989) ,  Vector2(285.957, 881.953) ,  Vector2(348.444, 848.706) , 
               Vector2(684.413, 823.087) ,  Vector2(806.888, 779.872) ,  Vector2(832.825, 729.747) ,  
               Vector2(820.772, 681.931) ,  Vector2(772.271, 669.529) ,  Vector2(691.177, 680.119) ,  
               Vector2(588.933, 705.721) ,  Vector2(469.788, 698.801) ,  Vector2(403.041, 656.489) , 
               Vector2(363.364, 581.619) ,  Vector2(352.519, 513.937) ,  Vector2(364.808, 460.497) , 
               Vector2(415.761, 448.392) ,  Vector2(633.858, 488.125) ,  Vector2(727.696, 488.498) , 
               Vector2(803.688, 451.328) ,  Vector2(858.655, 282.654) ,  Vector2(938.476, 194.408) , 
               Vector2(1022.09, 171.665) ,  Vector2(1142.49, 211.706) ,  Vector2(1200.15, 259.068) ,  
               Vector2(1320.3, 377.557) ,  Vector2(1397.47, 405.683) ,  Vector2(1475.19, 376.782) ,  
               Vector2(1609.79, 259.404) ,  Vector2(1670.68, 260.261) ,  Vector2(1714.81, 316.775) ,  
               Vector2(1706.16, 403.62) ,  Vector2(1658.75, 449.782), Vector2(1226.28, 739.132)]

# Extract x and y coordinates
x = [point.x for point in track_lines]
y = [-1 * point.y for point in track_lines]

# Fit a spline to the data
tck1, u1 = interpolate.splprep([x, y], s=0, per=1)
tck2, u2 = interpolate.splprep([x, y], s=123, per=1)


# Generate new points along the spline
unew = np.linspace(0, 1, 500)  # 500 new points
unew = np.linspace(0, 1, 3* len(track_lines))  # 500 new points
out1 = interpolate.splev(unew, tck1)
out2 = interpolate.splev(unew, tck2)

# Plot the original points and the interpolated spline
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'o', label='Data points', markersize=5)

plt.plot(x, y, label="lines")

# plt.plot(out1[0], out1[1], label='Interpolated Spline')
plt.plot(out2[0], out2[1], label='Interpolated Spline')

plt.legend()
plt.title('Track Lines Spline Interpolation')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()

