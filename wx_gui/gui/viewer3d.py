from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from wx import *
from wx.glcanvas import *

import math  

class OpenGLCanvas(GLCanvas):
    def __init__(self, parent):
        GLCanvas.__init__(self, parent, -1)
        
        self.init = False
        self.context = GLContext(self)
        self.rotation_angle_x = 0.0
        self.rotation_angle_y = 0.0
        self.camera_distance = 2.5  # Zoom mais próximo
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.last_mouse_pos = None

        self.Bind(EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(EVT_MOTION, self.OnMouseMove)
        self.Bind(EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(EVT_PAINT, self.OnPaint)
        self.Bind(EVT_SIZE, self.OnResize)
        self.Bind(EVT_KEY_DOWN, self.handleKeypress)

    def initRendering(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.95, 0.95, 0.95, 1.0)
        glMatrixMode(GL_MODELVIEW)

    def OnMouseWheel(self, event):
        delta = event.GetWheelRotation() / event.GetWheelDelta()
        self.camera_distance -= delta * 0.2 # Adjust sensitivity as needed
        self.Refresh()

    def OnLeftDown(self, event):
        #print("LMB DOWN")

        self.CaptureMouse()
        self.last_mouse_pos = event.GetPosition()

    def OnLeftUp(self, event):
        #print("LMB UP")
        if self.HasCapture():
            self.ReleaseMouse()

    def OnRightDown(self, event):
        #print("RMB DOWN")
        self.CaptureMouse()
        self.last_mouse_pos = event.GetPosition()
        event.Skip()

    def OnRightUp(self, event):
        #print("RMB UP")
        if self.HasCapture():
            self.ReleaseMouse()
        event.Skip()

    def OnMouseMove(self, event):
        if event.Dragging():
            mouse_pos = event.GetPosition()
            if self.last_mouse_pos:
                delta_x = mouse_pos.x - self.last_mouse_pos.x
                delta_y = mouse_pos.y - self.last_mouse_pos.y
                sensitivity = 0.1  # Adjust sensitivity as needed
                if event.RightIsDown():  # Check if right mouse button is down for panning
                    # Adjust the pan calculation based on the camera distance
                    self.pan_x += delta_x * sensitivity * self.camera_distance * 0.1
                    self.pan_y -= delta_y * sensitivity * self.camera_distance * 0.1
                elif event.LeftIsDown():  # Check if left mouse button is down for rotation (orbit)
                    self.rotation_angle_x += delta_y * sensitivity *2
                    self.rotation_angle_y += delta_x * sensitivity *2
                self.Refresh()
            self.last_mouse_pos = mouse_pos
        event.Skip()


    def OnPaint(self, event):
        if not self.init:
            self.init = True
            self.SetCurrent(self.context)
            self.initRendering()
            self.OnResize(0)
        
        tool_max_width = int(self.Parent.screenWidth / 3) - 400
        tool_max_height = int(self.Parent.screenHeight / 5)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        ambient_light = [1, 1, 1, 0.5]  # Increase ambient light intensity
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_light)

        light_position = [0.0, 50.0, 50, 1.0]  # Adjusted light position
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        material_color = [1, 0.8, 0.8, 0.5]
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, material_color)

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

        # Apply panning
        glTranslatef(self.pan_x, self.pan_y, 0.0)

        # gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z)
        gluLookAt(0, 0, center_of_rotation + self.camera_distance,
                0, 0, center_of_rotation,
                0, 1, 0)

        glRotatef(self.rotation_angle_x, 1, 0, 0)
        glRotatef(self.rotation_angle_y, 0, 1, 0)

        glTranslatef(0, 0, -center_of_rotation) # Move the object to the center of the screen

        glColor3f(1.0, 0.5, 0.0)
        self.draw_cylinder(scaled_values["D1"], scaled_values["L1"], 100)
        glTranslatef(0.0, 0.0, scaled_values["L1"])
        glColor3f(0.5, 0.5, 0.5)
        self.draw_cylinder(scaled_values["D2"], scaled_values["L2"] - scaled_values["L1"], 100)
        glTranslatef(0.0, 0.0, scaled_values["L2"] - scaled_values["L1"])
        self.draw_cylinder(scaled_values["D3"], scaled_values["L3"]-scaled_values["L2"], 100)

        self.SwapBuffers()


    def OnResize(self, event):
        if not self.init:
            return
        
        w, h = self.GetSize()
        glViewport(0, 0, w, h)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45., float(w)/float(h), 1., 200.)

        self.OnPaint(-1)

    def handleKeypress(self, event):
        key = event.GetUnicodeKey()
        if key == 27:
            exit()

    def draw_cylinder(self, radius, height, slices=100):
        glBegin(GL_QUAD_STRIP)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            glVertex3f(x, y, 0)
            glVertex3f(x, y, height)
        glEnd()

        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()

        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, height)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, height)
        glEnd()

class test(wx.Frame):
    def __init__(self):
        """
        Initialisation de la frame utilisée pour afficher le canvas openGL
        """
        wx.Frame.__init__(self, None, \
                          title = "Basic Shapes", \
                          size = (506, 432))
        aire = OpenGLCanvas(self)
        panel = wx.Panel(self, -1, size = (100, 432))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(aire, 1, wx.EXPAND)
        sizer.Add(panel, 0)
        
        self.SetSizer(sizer)

        self.Show()
