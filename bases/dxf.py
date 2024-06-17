import math
import ezdxf
import sys

try:
    #doc = ezdxf.readfile("./wx_gui/importTools/334850.dxf")
    #doc = ezdxf.readfile("./wx_gui/importTools/334850.dxf")
    #doc = ezdxf.readfile("./wx_gui/importTools/334937.dxf")
    #doc = ezdxf.readfile("./wx_gui/importTools/46440.dxf")
    #doc = ezdxf.readfile("./wx_gui/importTools/41907.dxf")
    #threadmill
    doc = ezdxf.readfile("./wx_gui/importTools/961170.dxf")
    

    
except IOError:
    print(f"Not a DXF file or a generic I/O error.")
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f"Invalid or corrupted DXF file.")
    sys.exit(2)

# Initialize a list to store the points
points = []

# Iterate over all entities in modelspace
msp = doc.modelspace()
for e in msp:
    if e.dxftype() == "LINE":
        start = e.dxf.start
        end = e.dxf.end

        # Add the start and end points to the list
        points.append(start)
        points.append(end)

# Print the list of points
for point in points:
    print(point)

#try to get tool type from dxf file

#got this coords from dxf file
    """(-3.5588190451, 0.4015741737, 0.0)
(-7.6582000372, 1.5, 0.0)
(-7.6582000372, 1.5, 0.0)
(-37.7, 1.5, 0.0)
(-37.7, 1.5, 0.0)
(-38.0, 1.2, 0.0)
(-38.0, 1.2, 0.0)
(-38.0, -1.2, 0.0)
(-38.0, -1.2, 0.0)
(-37.7, -1.5, 0.0)
(-37.7, -1.5, 0.0)
(-7.6582000372, -1.5, 0.0)
(-7.6582000372, -1.5, 0.0)
(-3.5588190451, -0.4015741737, 0.0)
(-3.3, -0.3675, 0.0)
(-0.2249123402, -0.3675, 0.0)
(-0.2249123402, -0.3675, 0.0)
(-0.1282061701, -0.535, 0.0)
(-0.1282061701, -0.535, 0.0)
(-0.0967061701, -0.535, 0.0)
(-0.0967061701, -0.535, 0.0)
(0.0, -0.3675, 0.0)
(0.0, -0.3675, 0.0)
(0.0, 0.3675, 0.0)
(0.0, 0.3675, 0.0)
(-0.0967061701, 0.535, 0.0)
(-0.0967061701, 0.535, 0.0)
(-0.1282061701, 0.535, 0.0)
(-0.1282061701, 0.535, 0.0)
(-0.2249123402, 0.3675, 0.0)
(-0.2249123402, 0.3675, 0.0)
(-3.3, 0.3675, 0.0)"""

import math

class Coords:
    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z
    
    @property
    def vector(self):
        return [self._x, self._y, self._z]
        

# Convert points to Coords objects
points = [Coords(*point) for point in points]

# Initialize the most left, right, up, and down points
most_left = most_right = most_up = most_down = points[0]

#init max and min values
max_x = max_y = max_z = 0
min_x = min_y = min_z = 0

for i in range(0, len(points), 2):
    #transform coords to vector
    vector = points[i].vector
    print("vector :: ", vector)
    #get max and min values
    if vector[0] > max_x:
        max_x = vector[0]
    if vector[1] > max_y:
        max_y = vector[1]
    if vector[2] > max_z:
        max_z = vector[2]
    if vector[0] < min_x:
        min_x = vector[0]
    if vector[1] < min_y:
        min_y = vector[1]
    if vector[2] < min_z:
        min_z = vector[2]
print("max_x :: ", max_x)
print("max_y :: ", max_y)
print("max_z :: ", max_z)
print("min_x :: ", min_x)
print("min_y :: ", min_y)
print("min_z :: ", min_z)
# Get the most left point
if points[i].x < most_left.x:
    most_left = points[i]
if points[i].x < most_left.x:
    most_left = points[i]
# Get the most right point
if points[i].x > most_right.x:
    most_right = points[i]
# Get the most up point
if points[i].y > most_up.y:
    most_up = points[i]
# Get the most down point
if points[i].y < most_down.y:
    most_down = points[i]






