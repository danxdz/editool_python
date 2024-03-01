import ezdxf
import sys
import wx
import math

try:

    # Create a new instance of the wx.App. The App object must be created first, before any other GUI objects are created.
    app = wx.App()
    

    #select .dxf file
    file = wx.FileDialog(None, "Choose a file", wildcard="DXF files (*.dxf)|*.dxf", style=wx.FD_OPEN)
    if file.ShowModal() == wx.ID_OK:
        print(file.GetPath())
        doc = ezdxf.readfile(file.GetPath())
    else:
        print("No file selected")
        sys.exit(0)  
        
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
#for point in points:
    #print(point)

# Initialize variables to store information about the tool
d1, d2, d3, L1, L2, L3 = 0, 0, 0, 0, 0, 0

d = []
d_x = []
l = []

# Iterate over the points grouped by segments
for i in range(0, len(points), 2):
    start = points[i]
    end = points[i + 1]

    # Calculate the length of the segment
    lengthX = end[0] - start[0]
    lengthY = end[1] - start[1]

    if lengthX == 0 and abs(lengthY) > 0:
        print(f"start: {start}, end: {end} Vertical line {lengthX} :: {lengthY}")
        d.append(abs(lengthY))
        d_x.append(abs(start[0]))
    elif lengthY == 0 and abs(lengthX) > 0:
        print(f"start: {start}, end: {end} Horz line {lengthX} :: {lengthY}")
        l.append(abs(lengthX))
    else:
        print(f"start: {start}, end: {end} Diagonal line {lengthX} :: {lengthY}")

print(f":: d :: {d} :: d_x :: {d_x}")

if d_x[0] == 0:
    #rip the first element
    d_x.pop(0)
if len(d_x) == 2 and len(d) > 2:
    #rip the last element
    if d[len(d)-1] < d[len(d) - 2]:
        d.pop()        


print(f":: d :: {d} :: d_x :: {d_x}")