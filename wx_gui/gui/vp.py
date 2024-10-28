import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_TIMES_ROMAN_24
from OpenGL.GLU import *
from OpenGL.GLUT import glutBitmapCharacter

import math

class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        attribs = [
            glcanvas.WX_GL_RGBA, 
            glcanvas.WX_GL_DOUBLEBUFFER, 
            glcanvas.WX_GL_DEPTH_SIZE, 24,
            glcanvas.WX_GL_SAMPLES, 4  # Habilitar anti-aliasing
        ]
        super(OpenGLCanvas, self).__init__(parent, attribList=attribs)
        self.context = glcanvas.GLContext(self)
   
        self.init = False
        self.pan_x = 0
        self.pan_y = -1.2
        self.last_mouse_pos = None

        self.camera_distance = 5  # Distância da câmera (para zoom)
        self.camera_angle_x = 0  # Ângulo de rotação em torno do eixo X
        self.camera_angle_y = 135 # Ângulo de rotação em torno do eixo Y


        # Eventos do mouse
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)  # Para zoom
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)     # Para rotação e pan
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)     # Para ativar rotação
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)         # Para desativar rotação
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)   # Para ativar pan
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       # Para desativar pan

        self.timer = wx.Timer(self)
        self.timer.Start(16)  # Atualiza a tela a cada 16 ms (~60 FPS)

        self.is_rotating = False
        self.is_panning = False

    def InitGL(self):
        # Configurações básicas de OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)  # Ativar anti-aliasing (suavização de bordas)
        glClearColor(0.95, .95, .95, 1)  # Fundo branco (RGBA)
        
        glutInit()

    def OnPaint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # added Pan
        glTranslatef(self.pan_x, self.pan_y, -self.camera_distance)
        # added Orbiting
        glRotatef(self.camera_angle_x, 1, 0, 0)
        glRotatef(self.camera_angle_y, 0, 1, 0)

        #set colors
        gray = (0.5, 0.5, 0.5)
        drakGray = (0.3, 0.3, 0.3)
        orange = (1, 0.5, 0)
        black = (0, 0, 0)

        cutContourColor = black
        cutFaceColor = orange
        cutTipColor = orange

        neckContourColor = black
        neckFaceColor = gray
        neckTipColor = gray

        toolContourColor = black
        toolFaceColor = drakGray
        toolTipColor = drakGray

        slices = 60

        lineW = 0.05

        tool_max_width = int(self.Parent.screenWidth / 3) - 400
        tool_max_height = int(self.Parent.screenHeight / 5)

        scale_width = (tool_max_width) / self.Parent.selected_tool.L3
        scaled_values = {
            'D1': int((self.Parent.selected_tool.D1 * scale_width) / 2) / 100,
            'D2': int((self.Parent.selected_tool.D2 * scale_width) / 2) / 100 if self.Parent.selected_tool.D2 else int(((self.Parent.selected_tool.D1 - 0.2) * scale_width) / 2) / 100,
            'D3': int((self.Parent.selected_tool.D3 * scale_width) / 2) / 100,
            'L1': int(self.Parent.selected_tool.L1 * scale_width) / 100,
            'L2': int(self.Parent.selected_tool.L2 * scale_width) / 100 if self.Parent.selected_tool.L2 else 0,
            'L3': int(self.Parent.selected_tool.L3 * scale_width) / 100,
        }

        center_of_rotation = scaled_values['L3'] / 2
        
        lineW = (lineW * scale_width)/100
   
        l2 =  scaled_values["L2"] - scaled_values["L1"]
        l3 = scaled_values["L3"]-scaled_values["L2"]

        # get tool type
        toolType = self.Parent.selected_tool.toolType

        glTranslatef(0, 0, -center_of_rotation) # Move the object to the center of the screen
        


        self.DrawCoordinateSystem(scaled_values["D1"]*1.5)  # You can adjust the size parameter as needed


        self.DrawRule(self.Parent.selected_tool.L3, scaled_values["L3"], scaled_values["D3"], 1*scale_width /100) 

        #build text
        text = "D1:" + str(self.Parent.selected_tool.D1) + "\n" + " L1:" + str(self.Parent.selected_tool.L1) 
        self.drawText(0, 0.2, -.8, (1, -0.25), text)
                
        neck = False

        # Draw the tool
        # cut
        if toolType == 2:
            # Translate to the middle of the first cylinder
            
            glTranslatef(0, 0, scaled_values["D1"])

            # Draw a sphere
            self.DrawSphere(scaled_values["D1"], slices, cutFaceColor)
            
            #glTranslatef(0, 0, scaled_values["D1"] )
            # Draw a cylinder for the cutting part if it is greater than sphere radius
            if scaled_values["D1"]/2 < scaled_values["L1"]:
                self.DrawCylinder(scaled_values["D1"], scaled_values["L1"] - lineW - (scaled_values["D1"]), slices, cutFaceColor)
                # Translate to the end of the cutting part
                glTranslatef(0, 0, scaled_values["L1"] - lineW - (scaled_values["D1"]))
                self.DrawCylinder(scaled_values["D1"], lineW , slices, black)
            neck = True
                
        elif toolType == 6: # center drill
            # Draw the tip face
            #calc the height of the cone 118deg
            cone_height = scaled_values["D1"]/math.tan(math.radians(59))
            
            self.DrawCone(scaled_values["D1"], cone_height-lineW, slices, cutFaceColor)
            glTranslatef(0, 0, cone_height-lineW)
            self.DrawCylinder(scaled_values["D1"], lineW, slices, cutContourColor)
            glTranslatef(0, 0, lineW)
            #draw the cylinder
            self.DrawCylinder(scaled_values["D1"], scaled_values["L1"]-cone_height-lineW, slices, cutFaceColor)
            glTranslatef(0, 0, scaled_values["L1"]-cone_height-lineW)
            self.DrawCylinder(scaled_values["D1"], lineW, slices, cutContourColor)
            glTranslatef(0, 0, lineW)
            #draw the cone angle
            self.DrawConeAngle(scaled_values["D1"], scaled_values["D2"]-lineW,self.Parent.selected_tool.chamfer/2, slices, cutFaceColor)
            glTranslatef(0, 0, scaled_values["D1"]/math.tan(math.radians(self.Parent.selected_tool.chamfer/2))-lineW)
            self.DrawCylinder(scaled_values["D2"], lineW, slices, cutContourColor)
            glTranslatef(0, 0, lineW)
            self.DrawCylinder(scaled_values["D2"], l2-lineW-cone_height-scaled_values["L1"], slices, cutFaceColor)
            glTranslatef(0, 0, l2-lineW-cone_height-scaled_values["L1"])
       
            neck = False

        else:
            
            # Draw the tip face
            self.DrawFaces(0,scaled_values["D1"]-lineW, slices, cutFaceColor, lineW)
            # Draw the tip face contour
            self.DrawContourFaces(scaled_values["D1"], slices, cutContourColor, lineW)
            # Draw the cylinder black
            self.DrawCylinder(scaled_values["D1"], lineW, slices, cutContourColor)
            # Translate to the end of the small cylinder
            glTranslatef(0, 0, lineW)
            # Draw the cylinder with the face color
            self.DrawCylinder(scaled_values["D1"], scaled_values["L1"] - lineW, slices, cutFaceColor)
            # Translate to the end of the cut
            glTranslatef(0, 0, scaled_values["L1"] - lineW)
            # Draw the contour cylinder
            self.DrawCylinder(scaled_values["D1"], lineW, slices, cutContourColor)

            neck = True
        
        if neck :
            glTranslatef(0, 0, lineW)        

            self.DrawFaces(scaled_values["D2"]-lineW,scaled_values["D1"]-lineW, slices, gray, lineW)
            # Draw the tip face contour
            self.DrawContourFaces(scaled_values["D1"], slices, cutContourColor, lineW)
            self.DrawContourFaces(scaled_values["D2"], slices, cutContourColor, lineW)

            self.DrawCylinder(scaled_values["D2"], lineW, slices, cutContourColor)
            glTranslatef(0, 0, lineW)        

            # Draw the neck part of the tool
            self.DrawCylinder(scaled_values["D2"], l2 - lineW, slices, neckFaceColor)
            # Translate to the end of the neck part
            glTranslatef(0, 0, l2 - lineW)
            # Draw the neck contour
            self.DrawCylinder(scaled_values["D2"], lineW, slices, neckContourColor)
            # Translate to the end of the neck contour
            glTranslatef(0, 0, lineW)
            # Draw the neck tip face
            self.DrawFaces(scaled_values["D2"]+lineW, scaled_values["D3"]-lineW, slices, neckTipColor, lineW)
        
        # Draw the neck tip face contour
        self.DrawContourFaces(scaled_values["D3"], slices, neckContourColor, lineW)
        # Draw the neck contour cylinder
        self.DrawCylinder(scaled_values["D3"], lineW, slices, neckContourColor)
        # Translate to the end of the neck contour cylinder
        glTranslatef(0, 0, lineW)
        # Draw the main body of the tool
        self.DrawCylinder(scaled_values["D3"], l3 - (lineW * 2), slices, toolFaceColor)
        # Translate to the end of the main body
        glTranslatef(0, 0, l3 - lineW)
        # Draw the main body contour
        self.DrawCylinder(scaled_values["D3"], lineW, slices, toolContourColor)
        # Translate to the end of the main body contour
        glTranslatef(0, 0, lineW)
        # Draw the main body tip face
        self.DrawFaces(scaled_values["D3"],0, slices, toolTipColor, lineW)
        # Draw the main body tip face contour
        self.DrawContourFaces(scaled_values["D3"], slices, toolContourColor, lineW)
        """
        """
       
        self.SwapBuffers()



    def DrawSphere(self, radius, slices,color):
        # Configura a cor da esfera
        glColor3f(*color)
        # Desenha a esfera
        quad = gluNewQuadric()
        glPushMatrix()
        gluSphere(quad, radius, slices, slices)
        glPopMatrix()
        

    def DrawTorique(self, innerRadius, outerRadius, slices, loops, color):
        #glutSolidTorus( innerRadius , outerRadius , sides , rings )
        glColor3f(*color)
        quad = gluNewQuadric()

        glPushMatrix()
        glutSolidTorus(quad,0, 1, 5, 2)
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

    def DrawCone(self, radius, height, slices, color):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        #glTranslatef(0, 0, -height / 2)  # Mover o cilindro para o centro
        gluCylinder(quad, 0, radius, height, slices, 1)
        glPopMatrix()

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

    def drawText(self, x, y, z, color, text):
        # Save current attributes
      

        # Draw 3D numbers
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(self.camera_angle_y*-1, 0, 1, 0)
        glRotatef(self.camera_angle_x*-1, 1, 0, 0)
        glScalef(0.0004, 0.0004, 0.0004)
        for line in text.split("\n"):
            for char in line:
                glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN, ord(char))
            

        glPopMatrix()


    def DrawRule(self, l3, size=1.0,diam=1.0, step=1.0):
        """
        Draw a rule with numbers
        Args:
            size: Length of the rule
            step: Step between numbers
        """
        # Save current attributes
        glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT)
        glLineWidth(2.0)


        # Draw rule
        glBegin(GL_LINES)
        for i in range(int(size*1.5 / step) + 1):
            if i > l3:
                break
            glColor3f(0.8, 0.8, 0.8)
            #change color every 10
            mult = 1.3
            if i % 10 == 0:
                mult=1.5
                #change color to black
                glColor3f(0.5, 0.5, 0.5)
            elif i % 5 == 0:
                mult=1.4
                glColor3f(0.6, 0.6, 0.6)


            glVertex3f(0, -diam-(diam/6), i * step)
            glVertex3f(0, -diam*mult,i * step )
        glEnd()

        # Draw 3D numbers
        for i in range(int(size / step) + 1):
            
            if i % 10 == 0:
                glPushMatrix()
                glTranslatef(0, -diam*1.5-0.06, i * step-0.02)
                glRotatef(-90, 0, 1, 0)
                glScalef(0.0005, 0.0005, 0.001)
                glColor3f(0.2, 0.2, 0.2)
                if i < 100:
                    glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(str(i // 10)))
                elif i >= 100:
                    #100 gets to 10 divise into 2 numbers to get 1 and 0
                    glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(str(i // 100)))
                    glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(str((i // 10) % 10)))


                
                glPopMatrix()


        
        # Restore previous attributes
        glPopAttrib()


    def DrawCoordinateSystem(self, size=1.0):
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
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-size, 0.0, 0.0)
        
        # Y axis - Green
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, size)
        
        # Z axis - Blue
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, size, 0.0)
        
        
        glEnd()

        red = (1.0, 0.0, 0.0)
        glTranslatef(-size-(size/5), 0, 0)
        glRotatef(90, 0, 1, 0)
        self.DrawCone(size/15, size/5, 20, red)
        #self.drawText(10, 10, (1.0, 0.0, 0.0), "X")
        glRotatef(-90, 0, 1, 0)
        glTranslatef(size+(size/5), 0, 0)

        blue = (0.0, 0.0, 1.0)
        glTranslatef(0, size+(size/5),0)
        glRotatef(90, 1, 0, 0)
        self.DrawCone(size/15, size/5, 20, blue)
        #self.drawText(10, 50, (0.0, 0.0, 1.0), "Z")
        glRotatef(-90, 1, 0, 0)
        glTranslatef(0, -size-(size/5),0)
        
        green = (0.0, 1.0, 0.0)
        glTranslatef(0, 0, size+(size/5))
        glRotatef(180, 0, 1, 0)
        self.DrawCone(size/15, size/5, 20, green)
        #self.drawText(10, 30, (0.0, 1.0, 0.0), "Y")
        glRotatef(-180, 0, 1, 0)
        glTranslatef(0, 0, -size-(size/5))

        


        # Draw axis labels

        # Restore previous attributes
        glPopAttrib()


    def OnSize(self, event):
        size = self.Parent.GetSize()
        self.SetCurrent(self.context)

        glViewport(0, 0, size.width, size.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, size.width / size.height, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def OnTimer(self, event):
        self.Refresh()  # Atualiza a tela constantemente

    def OnMouseWheel(self, event):
        # Ajustar o zoom com base na rolagem do mouse
        delta = (event.GetWheelRotation() / event.GetWheelDelta())/4
        self.camera_distance -= delta
        if self.camera_distance < 1:
            self.camera_distance = 1  # Limite mínimo de zoom
        if self.camera_distance > 50:
            self.camera_distance = 50  # Limite máximo de zoom
        self.Refresh()

    def OnMouseMotion(self, event):
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.GetPosition()

        current_pos = event.GetPosition()
        dx = current_pos.x - self.last_mouse_pos.x
        dy = current_pos.y - self.last_mouse_pos.y

        if self.is_rotating:
            # Rotacionar a cena com o movimento do mouse
            self.camera_angle_x += dy * 0.5
            self.camera_angle_y += dx * 0.5
        elif self.is_panning:
            # Pan com movimento do mouse
            self.pan_x += dx * 0.01
            self.pan_y -= dy * 0.01

        self.last_mouse_pos = current_pos
        self.Refresh()

    def OnLeftDown(self, event):
        # Começar a rotacionar
        self.is_rotating = True
        self.CaptureMouse()

    def OnLeftUp(self, event):
        # Parar de rotacionar
        if self.is_rotating:
            self.is_rotating = False
            self.ReleaseMouse()

    def OnRightDown(self, event):
        # Começar o pan
        self.is_panning = True
        self.CaptureMouse()

    def OnRightUp(self, event):
        # Parar o pan
        if self.is_panning:
            self.is_panning = False
            self.ReleaseMouse()


class OpenGLFrame(wx.Frame):
    def __init__(self, parent, title):
        super(OpenGLFrame, self).__init__(parent, title=title, size=(800, 600))
        
        self.canvas = OpenGLCanvas(self)
        self.Show()

class MyApp(wx.App):
    def OnInit(self):
        frame = OpenGLFrame(None, "Renderização OpenGL com Zoom, Rotação e Pan")
        frame.Show()
        return True

#app = MyApp(False)
#app.MainLoop()
