import math
import sys
import os

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

#from stl import mesh
'''
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.IFSelect import IFSelect_RetDone'''



class glObjects:
    def __init__(self, Parent):
        self.Parent = Parent
        self.camera_angle_x = 0
        self.camera_angle_y = 0
        #self.scale = self.Parent.scale_width

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
        diametre 
        #need to calculate the center of the sphere so they stay aligned to tool diameter
        for i in range(0, slices):
            glPushMatrix()
            glRotatef(i*(360/slices), 0, 0, 1)
            glTranslatef(diametre-r, 0, 0)
            gluSphere(quad, r, slices, slices)
            glPopMatrix()

        
        glPopMatrix()


    def DrawContourFaces(self, radius,slices, color,lineW):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        gluDisk(quad, radius-lineW, radius, slices, 10)
        glPopMatrix()

    def DrawFaces(self, in_radius, radius,slices, color,lineW):
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

    def DrawCone(self, radius, height, slices, color= (1.0, 0.0, 0.0)):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        #glPushMatrix()
        #glTranslatef(0, 0, -height / 2)  # Mover o cilindro para o centro
        gluCylinder(quad, 0, radius, height, slices, 1)
        #glPopMatrix()

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

    def drawText(self, x, y, z, color, text=""):
        
        self.camera_angle_x = self.Parent.camera_angle_x
        self.camera_angle_y = self.Parent.camera_angle_y
        #print(self.camera_angle_x, self.camera_angle_y)
        self.scale = 0.0006#self.Parent.scale_width/8000

        # Draw 3D numbers
        glPushMatrix()
        glRotatef(self.camera_angle_y*-1, 0, 1, 0)
        glRotatef(self.camera_angle_x*-1, 1, 0, 0)
        glScalef(self.scale, self.scale, self.scale)
        glTranslatef(x-0.022, y-.022, z-.022)

        black = (0, 0, 0)

        glColor3f(*color)
        for line in text.split("\n"):
            for char in line:
                
                glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN, ord(char))

        glPopMatrix()

        

    def DrawRule(self, l3, size=1.0, diam=1.0, step=1.0,units=0):
        """
        Draw a rule with numbers
        Args:
            size: Length of the rule
            step: Step between numbers
        """
        # Save current attributes
        glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT)
        glLineWidth(2.0)

        # Rotacionar a régua para posicioná-la corretamente
        glPushMatrix()
        glRotatef(self.camera_angle_x * -1, 0, 0, 1)

        # Draw rule lines
        glBegin(GL_LINES)
        for i in range(int(size * 1.5 / step) + 1):
            if i > l3:
                break
            # Define a cor padrão
            glColor3f(0.8, 0.8, 0.8)
            mult = 1.3
            if i % 10 == 0:
                mult = 1.5
                glColor3f(0.5, 0.5, 0.5)
            elif i % 5 == 0:
                mult = 1.4
                glColor3f(0.6, 0.6, 0.6)
            glVertex3f(0, -diam - (diam / 6), i * step)
            glVertex3f(0, -diam * mult, i * step)
        glEnd()

        # Draw 3D numbers
        for i in range(int(size / step) + 1):
            if i % 10 == 0:
                # Dentro do loop de desenho dos números
                glPushMatrix()
                # Posicionar o texto na posição correta ao longo da régua
                glTranslatef(0, -diam * mult - 0.12, i * step-0.02)

                # Cancelar a rotação aplicada à régua
                glRotatef(self.camera_angle_x, 0, 0, 1)  # Cancela a rotação da régua sobre Z



                # Cancelar as rotações da câmera para que o texto fique de frente
                glRotatef(-self.camera_angle_y, 0, 1, 0)
                glRotatef(-self.camera_angle_x, 1, 0, 0)

                # Escalar o texto para um tamanho apropriado
                glScalef(0.00055, 0.00055, 0.00055)
                glColor3f(0.5, 0.5, 0.5)

                # Converter o número em string
                if units == 0:
                    t = int(i /10)
                    text = f"{t}"
                else:
                    text = f"{i}"
            
                for c in text:
                    glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(c))

                glPopMatrix()

        glPopMatrix()  # Fecha o PushMatrix da régua

        # Restore previous attributes
        glPopAttrib()


    def DrawCoordinateSystem(self, size=1.0):
        """
        Draw a coordinate system with X (red), Y (green), and Z (blue) axes
        Args:
            size: Length of the axes
        """
        # Save current attributes
        #glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT)
        glLineWidth(2.0)

        # Draw axes
        glBegin(GL_LINES)
        
        # X axis - Red
        red = (0.9, 0.1, 0.1)
        glColor3f(*red) 
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-size, 0.0, 0.0)
        
        # Y axis - Green
        green = (0.1, 0.9, 0.1)
        glColor3f(*green)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, size)
        
        # Z axis - Blue
        blue = (0.1, 0.1, 0.9)
        glColor3f(*blue)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, size, 0.0)
        
        
        glEnd()

        glTranslatef(-size-(size/5), 0, 0)
        glRotatef(90, 0, 1, 0)
        self.DrawCone(size/15, size/5, 20, red)
        glRotatef(-90, 0, 1, 0)

        red = (1, 0, 0)
        self.drawText(0, 0,0 , red, "X")
        glTranslatef(size+(size/5), 0, 0)

        glTranslatef(0, size+(size/5),0)
        glRotatef(90, 1, 0, 0)
        self.DrawCone(size/15, size/5, 20, blue)
        glRotatef(-90, 1, 0, 0)
        self.drawText(0, 0, 0, blue, "Z")
        glTranslatef(0, -size-(size/5),0)
        
        glTranslatef(0, 0, size+(size/5))
        glRotatef(180, 0, 1, 0)
        self.DrawCone(size/15, size/5, 20, green)
        
        self.drawText(0, 0, 0, green, "Y")

        glRotatef(-180, 0, 1, 0)
        glTranslatef(0, 0, -size-(size/5))

        
        # Restore previous attributes
        #glPopAttrib()


    def Draw_stl(self):
        global your_mesh
        # Load the mesh
        #get run path
        path = os.path.dirname(os.path.realpath(__file__))

        your_mesh = mesh.Mesh.from_file(path+"\\myshape.stl")

        # Find the center of the mesh
        center = your_mesh.get_mass_properties()[1]
        
        # Draw the mesh scaled and in the correct position
        glPushMatrix()
        glScalef(self.Parent.scale_width/200,self.Parent.scale_width/200, self.Parent.scale_width/200)
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

'''    def Draw_step(self):

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
        print("Meshing completed.", myshape)'''