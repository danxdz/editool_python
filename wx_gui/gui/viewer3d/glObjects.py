import math
import sys
import os
from stl import mesh
import logging
import wx

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


import numpy as np

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopLoc import TopLoc_Location

class glObjects:
    def __init__(self, Parent):
        self.Parent = Parent
        self.camera_angle_x = 0
        self.camera_angle_y = 0
        #self.scale = self.Parent.scale_width

        self.angle_x = 0.0
        self.angle_y = 0.0
        self.zoom = 1.0
        self.mouse_down = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.vertices = []
        self.indices = []

        self.normals = None
        self.vertex_array = None
        self.index_array = None
        

    def DrawSphere(self, radius, slices,color):
        # Configura a cor da esfera
        glColor3f(*color)
        # Desenha a esfera
        quad = gluNewQuadric()
        glPushMatrix()
        gluSphere(quad, radius, slices, slices)
        glPopMatrix()
        

    def DrawTorique(self, diametre, r, slices, color):
        #glutSolidTorus( innerRadius , outerRadius , sides , rings )
        #make the torus out off spheres
        # Configura a cor da esfera
        glColor3f(*color)
        # Desenha a esfera
        quad = gluNewQuadric()
        glPushMatrix()

        glTranslatef(0, 0, r)
        #need to calculate the center of the sphere so they stay aligned to tool diameter
        for i in range(0, slices*2):
            glPushMatrix()
            glRotatef(i*(360/(slices*2)), 0, 0, 1)
            glTranslatef(diametre-r, 0, 0)
            gluSphere(quad, r, slices, slices)
            glPopMatrix()
        glPopMatrix()
        glTranslatef(0, 0, r)


    def DrawContourFaces(self, radius,slices, color):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        gluDisk(quad, radius, radius, slices, 10)
        glPopMatrix()

    def DrawFaces(self, in_radius, radius,slices, color):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        gluDisk(quad, in_radius, radius, slices, 10)
        glPopMatrix()

    def DrawCylinder(self, radius, height, slices, color):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        #glTranslatef(0, 0, -height / 2)  # Mover o cilindro para o centro
        gluCylinder(quad, radius, radius, height, slices, 1)
        glPopMatrix()
        glTranslatef(0, 0, height)

    def DrawCone(self, radius, height, slices, color= (1.0, 0.0, 0.0),r1=0):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        #glTranslatef(0, 0, -height)  # Mover o cilindro para o centro
        gluCylinder(quad, r1, radius, height, slices, 1)
        glPopMatrix()
        glTranslatef(0, 0, height)
        

    #draw cone with start an end diameter and angle to determine the height
    def DrawConeAngle(self, radius, end_radius, angle, slices, color):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        #glTranslatef(0, 0, -height / 2)  # Mover o cilindro para o centro
        gluCylinder(quad, radius, end_radius, radius/math.tan(math.radians(angle)), slices, 1)
        
        glPopMatrix()

    def drawText(self,canvas, x, y, z, color, text=""):
        
        #self.camera_angle_x = self.Parent.camera_angle_x
        #self.camera_angle_y = self.Parent.camera_angle_y
        #print(self.camera_angle_x, self.camera_angle_y)
        self.scale = 0.0002#self.Parent.scale_width/8000

        # Draw 3D numbers
        glPushMatrix()
        glRotatef(canvas.camera_angle_y*-1, 0, 1, 0)
        glRotatef(canvas.camera_angle_x*-1, 1, 0, 0)
        glScalef(self.scale, self.scale, self.scale)
        glTranslatef(x-0.022, y-.022, z-.022)

        black = (0, 0, 0)

        glColor3f(*color)
        for line in text.split("\n"):
            for char in line:
                
                glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN, ord(char))

        glPopMatrix()

        

    def DrawRule(self, canvas,  l3, size, diam=1.0, step=1.0,units=0):
        """
        Draw a rule with numbers
        Args:
            size: Length of the rule
            step: Step between numbers
        """
        # Save current attributes
        glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT)
        glLineWidth(2.5)

        glPushMatrix()
        glRotatef(canvas.camera_angle_x * -1, 0, 0, 1)
        glTranslatef(0, -diam/1.8, 0)

        # Draw rule lines
        glBegin(GL_LINES)
        for i in range(int(size * 1.5 / step) + 1):
            if i > l3:
                break
            # Define a cor padrão
            glColor3f(0.8, 0.8, 0.8) # mm lines
            mult = 1.3
            if i % 10 == 0:
                mult = 1.5
                glColor3f(0.5, 0.5, 0.5) # cm lines
            elif i % 5 == 0:
                mult = 1.4
                glColor3f(0.6, 0.6, 0.6) # half cm lines
            glVertex3f(0, -diam - (diam / 6), i * step)
            glVertex3f(0, -diam * mult, i * step)
        glEnd()

        # Draw 3D numbers
        for i in range(int(size / step)+10): # iterate over the size of the rule
            if (i % 10 == 0 or i == l3) and (i < l3+1): # check if the number is bigger than the limit to draw
                
                glPushMatrix()
                # text position
                glTranslatef(0, -diam * mult - 0.12, i * step-0.02)


                # cancel the rotation of the rule on Z
                glRotatef(canvas.camera_angle_x, 0, 0, 1) 

                # Rotate the text to face the camera
                glRotatef(-canvas.camera_angle_y, 0, 1, 0)
                glRotatef(-canvas.camera_angle_x, 1, 0, 0)

                # Scale the text
                glScalef(0.00052, 0.00052, 0.00052)
                glColor3f(0.5, 0.5, 0.5)
          

                if i == l3: 
                    # Draw the number make a for loop to draw the number if there are more than 1 digit
                    text = f"{int(i)/10}"
                    for c in text:
                        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(c))
                    glPopMatrix()

                elif i < l3:
                    # convert the number to string
                    if units == 0: #mm
                        t = int(i /10) #convert to cm
                        text = f"{t}" 
                    else:
                        text = f"{i}" 

                    for c in text:
                        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(c))

                    glPopMatrix() # Close the PushMatrix on the text
            

        glPopMatrix()  # Close the PushMatrix on the rule

        # Restore previous attributes
        glPopAttrib()


    def DrawCoordinateSystem(self, canvas,  size=1.0):
        """
        Draw a coordinate system with X (red), Y (green), and Z (blue) axes
        Args:
            size: Length of the axes
        """
        # Save current attributes
        glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT)
        glLineWidth(2.0)

        # Draw axes
        glBegin(GL_LINES)
        
        # X axis - Red
        red = (0.7, 0.1, 0.1)
        glColor3f(*red) 
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-size, 0.0, 0.0)
        
        # Y axis - Green
        green = (0.1, 0.7, 0.1)
        glColor3f(*green)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, size)
        
        # Z axis - Blue
        blue = (0.1, 0.1, 0.7)
        glColor3f(*blue)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, size, 0.0)
        
        
        glEnd()

        glTranslatef(-size-(size/5), 0, 0)
        glRotatef(90, 0, 1, 0)
        self.DrawCone(size/15, size/5, 20, red)
        glRotatef(-90, 0, 1, 0)

        red = (1, 0, 0)
        self.drawText(canvas, 250, 0, 0 , red, "X")
        glTranslatef(size+(size/5), 0, 0)

        glTranslatef(-size/5, size+(size/5),0)
        glRotatef(90, 1, 0, 0)
        self.DrawCone(size/15, size/5, 20, blue)
        glRotatef(-90, 1, 0, 0)
        self.drawText(canvas, 0, 250, 0, blue, "Z")
        glTranslatef(size/5, -size+(size/5),0)
        
        #glTranslatef(0, 0, size+(size/5))
        #glRotatef(180, 0, 1, 0)
        #self.DrawCone(size/15, size/5, 20, green)
        
        #self.drawText(canvas, 0, 0, 0, green, "Y")

        #glRotatef(-180, 0, 1, 0)
        #glTranslatef(0, 0, -size-(size/5))

        
        # Restore previous attributes
        glPopAttrib()


    def Draw_stl(self):
        global your_mesh
        # Load the mesh
        #get run path
        path = os.path.dirname(os.path.realpath(__file__))

        your_mesh = mesh.Mesh.from_file(path+"\\cube.stl")

        # Find the center of the mesh
        center = your_mesh.get_mass_properties()[1]
        
        # Draw the mesh scaled and in the correct position
        glPushMatrix()
        glScalef(self.Parent.scale_width/2000,self.Parent.scale_width/2000, self.Parent.scale_width/2000)
        glTranslatef(0, 0, center[2]*-1)
        #set color gray
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_TRIANGLES)
        for face in your_mesh.vectors:
            for vertex in face:
                glVertex3fv(vertex)
        glEnd()
        glTranslatef(0, 0, center[2])
        glPopMatrix() # Close the PushMatrix

    """def Draw_step(self):

        input_file  = 'cube.stp'
        output_file = 'myshape.stl'

        # Load STEP file
        step_reader = STEPControl_Reader()
        status = step_reader.ReadFile(input_file)

        if status == IFSelect_RetDone:
            print("STEP file read successfully.")
        else:
            print("Error: Cannot read STEP file.")
            sys.exit(1)

        # Transfer the roots (assemblies, shapes, etc.)
        step_reader.TransferRoot()
        myshape = step_reader.Shape()

        if myshape.IsNull():
            print("Error: The shape is null.")
            sys.exit(1)

        # Mesh the shape
        print("Meshing the shape...")
        BRepMesh_IncrementalMesh(myshape, 0.5)
        print("Meshing completed.", myshape)"""
    
    def read_step_file_geometry(self, step_file_path):
        self.vertices = []
        self.indices = []

        # Read the STEP file using pythonocc-core
        reader = STEPControl_Reader()
        status = reader.ReadFile(step_file_path)

        if status != IFSelect_RetDone:
            # Error reading the file
            logging.error("Error reading STEP file.")
            wx.MessageBox("Error reading STEP file.", "Error", wx.OK | wx.ICON_ERROR)
            sys.exit(1)

        reader.TransferRoot()
        # shape = reader.OneShape()
        # read multiple shapes
        shape = reader.Shape()
        step = reader.StepModel()
        print(step.Header)

        # Generate mesh with a defined deflection
        linear_deflection = 0.1  # Adjust as needed
        angular_deflection = 0.5
        BRepMesh_IncrementalMesh(shape, linear_deflection, False, angular_deflection)

        # Explore geometry to extract faces
        exp = TopologyExplorer(shape)
        index_offset = 0
        print(f"Total solids: {exp.number_of_solids()}")

        for face in exp.faces():
            location = TopLoc_Location()
            triangulation = BRep_Tool.Triangulation(face, location)
            if triangulation is None:
                continue

            trsf = location.Transformation()
            num_nodes = triangulation.NbNodes()
            num_triangles = triangulation.NbTriangles()

            # Add vertices
            for i in range(1, num_nodes + 1):
                pnt = triangulation.Node(i)
                pnt.Transform(trsf)
                self.vertices.append([pnt.X(), pnt.Y(), pnt.Z()])

            # Add indices
            for i in range(1, num_triangles + 1):
                tri = triangulation.Triangle(i)
                n1, n2, n3 = tri.Get()
                self.indices.extend([n1 - 1 + index_offset, n2 - 1 + index_offset, n3 - 1 + index_offset])

            index_offset += num_nodes

        print(f"Total vertices loaded: {len(self.vertices)}")
        print(f"Total indices loaded: {len(self.indices)}")

           
    def displayToolHolder(self, tool_slider, scale):

        if self.vertex_array is None or self.index_array is None or self.normals is None:
            #glPopMatrix()
            return

        glPushMatrix()

        glScalef(scale / 100, scale / 100, scale / 100)
        
        glColor4f(0.5, 0.5, 0.5, 1)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        light_position = [1.0, -1.0, 1.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        # Set the material properties
        ambient = [0.2, 0.2, 0.2, 1.0]
        diffuse = [0.8, 0.8, 0.8, 1.0]
        specular = [0.0, 0.0, 0.0, 1.0]
        shininess = 0.0
        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT, GL_SHININESS, shininess)


        # Use instance variables
        vertex_array = self.vertex_array
        index_array = self.index_array
        normals = self.normals

        #dec_z = 170 + tool_slider
        # get the minimum value of the z axis
        dec_z = (np.min(vertex_array, axis=0)[2] - tool_slider)*-1
        glTranslatef(0, 0, dec_z)

        # find the center of the tool
        #center = np.mean(vertex_array, axis=0)
        #print(center)
 
        # Enable and set vertex and normal arrays
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointerf(vertex_array)
        glNormalPointerf(normals)

        # Draw the geometry
        glDrawElements(GL_TRIANGLES, len(index_array), GL_UNSIGNED_INT, index_array)

        # Disable client states
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        glDisable(GL_LIGHTING)
        glPopMatrix()


            
    def compute_normals(self, vertices, indices):
        # Initialize normals array
        normals = np.zeros_like(vertices, dtype=np.float32)

        # Loop over each triangle
        for i in range(0, len(indices), 3):
            idx0, idx1, idx2 = indices[i:i+3]
            v0, v1, v2 = vertices[idx0], vertices[idx1], vertices[idx2]

            # Compute the normal for the triangle
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            normal_length = np.linalg.norm(normal)
            if normal_length != 0:
                normal /= normal_length

            # Add the normal to each vertex (for averaging)
            normals[idx0] += normal
            normals[idx1] += normal
            normals[idx2] += normal

        # Normalize the normals for each vertex
        normals_length = np.linalg.norm(normals, axis=1)
        normals_length[normals_length == 0] = 1  # Avoid division by zero
        normals /= normals_length[:, np.newaxis]

        return normals.astype(np.float32)
                

    def draw_canvas3d(self,canvas, tool, scale, last_click3d, x=0, y=0, z=0, w=20, h=7, color=(0.0, 0.0, 0.0)):
        """ Draw a rectangle canvas to draw text """

        if last_click3d not in [32716, 8355711, 5000268, 16250871]:
            return

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        # Switch to orthographic projection
        canvas_width, canvas_height = canvas.size.width, canvas.size.height
        glOrtho(0, canvas_width/6, 0, canvas_height/10, -1, 1)

        # Save the current modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Disable depth testing so the rectangle is always on top
        glDisable(GL_DEPTH_TEST)

        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Set the color and transparency
        glColor4f(0.6, 0.6, 0.6, 0.5)  # Semi-transparent grey

        # Set the position and size of the rectangle
        margin = 5  # Margin from the edges
        x = margin
        y = (canvas_height/10)-margin

       
        # Draw the rectangle
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y - h)
        glVertex2f(x, y - h)
        glEnd()

        # Draw border
        glColor4f(0.3, 0.3, 0.3, 0.8)  # Semi-transparent black
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y - h)
        glVertex2f(x, y - h)
        glEnd()
        
         # Restore the previous states
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        
        x += 2
        y -= 2

        
        out = f"{tool.name}"
        
        self.draw_text3d(x, y, z, [1, 1, 1], out)
        if last_click3d == 32716:
            #d1 l1
            out = f"D1: {tool.D1}"
            y -= 2
            self.draw_text3d(x, y, z, [1, 1, 1], out)
            out = f"L1: {tool.L1}"
            y -= 2
            self.draw_text3d(x, y, z, [1, 1, 1], out)
        elif last_click3d == 8355711:
            #d2 l2
            out = f"D2: {tool.D2}"
            y -= 2
            self.draw_text3d(x, y, z, [1, 1, 1], out)
            out = f"L2: {tool.L2}"
            y -= 2
        elif last_click3d == 5000268:
            #d3 l3
            out = f"D3: {tool.D3}"
            y -= 2
            self.draw_text3d(x, y, z, [1, 1, 1], out)
            out = f"L3: {tool.L3}"
            y -= 2
            self.draw_text3d(x, y, z, [1, 1, 1], out)
        elif last_click3d == 16250871:
            #holder
            out = "Holder:"
        
        # Restore the modelview matrix
        glPopMatrix()
        # Restore the projection matrix
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_text3d(self, x, y, z, color, text=""):
        """ Draw text on the 3D canvas using bitmap fonts """
        glPushMatrix()

        # Set the color
        glColor4f(0, 0, 0, 1)

        # Set the raster position
        glRasterPos3f(x, y, z)

        # Draw the text using GLUT bitmap fonts
        for line in text.split("\n"):
            for char in line:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
            # Move to the next line
            y -= 18  # Adjust line spacing as needed
            glRasterPos3f(x, y, z)

        glPopMatrix()


