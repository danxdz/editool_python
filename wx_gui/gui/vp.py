import wx
from wx.glcanvas import *

#specific imports for OpenGL to reduce the number of functions imported
import wx
from wx.glcanvas import *

# Specific imports for OpenGL to reduce the number of functions imported
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np
import math
import os

import numpy as np
import math
import os


class OpenGLCanvas(GLCanvas):
    def __init__(self, parent, gl):
        attribs = [
            WX_GL_RGBA, 
            WX_GL_DOUBLEBUFFER, 
            WX_GL_DEPTH_SIZE, 24,
            WX_GL_SAMPLES, 4  # Habilitar anti-aliasing
        ]
        super(OpenGLCanvas, self).__init__(parent, attribList=attribs)
        self.context = GLContext(self)

        self.gl = gl

        self.parent = parent

        glutInit( [] ) # Initialize GLUT


        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)       


        self.init = False

        self.size = self.GetSize()

        self.vertex_array = []
        self.index_array = []    
        self.normals = []


        self.units = parent.units

        self.last_mouse_pos = None
        self.pan_x = -.2
        self.pan_y = 0
        self.camera_distance = 3  # Distância da câmera (para zoom)
        self.camera_angle_x = 15  # Ângulo de rotação em torno do eixo X
        self.camera_angle_y = 135 # Ângulo de rotação em torno do eixo Y

        self.scale_width = 0

        # Eventos do mouse
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)  # Para zoom
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)     # Para rotação e pan
        self.Bind(wx.EVT_MIDDLE_DOWN, self.OnMidDown)     # Para ativar rotação
        self.Bind(wx.EVT_MIDDLE_UP, self.OnMidUp)         # Para desativar rotação
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)   # Para ativar pan
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       # Para desativar pan
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)    # Para seleção de objetos

        self.timer = wx.Timer(self)
        self.timer.Start(16)  # Atualiza a tela a cada 16 ms (~60 FPS)

        self.is_rotating = False
        self.is_panning = False
        self.is_resizing = False

        self.last_click3d = None

        #local_path = os.path.dirname(os.path.realpath(__file__))
        #step_file = os.path.join(local_path, 'cube2.stp')  # Replace with your STEP file

        #self.step = self.gl.read_step_file_geometry(step_file)

        self.step_path = None
        

    def InitGL(self):
        # Basic OpenGL configuration
        glEnable(GL_DEPTH_TEST) # Enable depth test
        glEnable(GL_MULTISAMPLE)  # Enable anti-aliasing
        glClearColor(0.97, .97, .97, 1)  # Set background color
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)

        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Set lighting
        self.setLighting()
        

    def setLighting(self):

        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)  # Enable the first light
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 1.0, 0.0, 0.0])  # Position of the light
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])   # Diffuse light color
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])  # Specular light color


        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, [0.0, -1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT2, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])

        glEnable(GL_LIGHT3)
        glLightfv(GL_LIGHT3, GL_POSITION, [-1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT3, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT3, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.3, 0.3, 0.5, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

        #need to setup light to GL_VERTEX_ARRAY
        glEnableClientState(GL_VERTEX_ARRAY)

        # set the shading model
        glShadeModel(GL_SMOOTH)


    def OnPaint(self, event):
        #self.SetCurrent(self.context)
        if self.Parent.selected_tool is None:
            return


        if not self.init:
            self.init = True
            self.InitGL()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear the buffers
        glLoadIdentity()  # Reset the modelview matrix

        self.setupScene()
        
        self.drawTool()
        


    def setupScene(self):

        # added Pan
        glTranslatef(self.pan_x, self.pan_y, -self.camera_distance)
        # added Orbiting
        glRotatef(self.camera_angle_x, 1, 0, 0)
        glRotatef(self.camera_angle_y, 0, 1, 0)

        # set colors
        self.gray = (0.5, 0.5, 0.5)
        self.drakGray = (0.3, 0.3, 0.3)
        self.orange = (.8, 0.5, 0)
        self.black = (0, 0, 0)
        #make a blue shiny material
        self.blueShiny = (0.3, 0.8, 0.95) 

        self.holderFaceColor = self.gray

        self.slices = 66

        tool_max_width = int(self.Parent.screenWidth / 3) - 400

        self.scale_width = (tool_max_width) / self.Parent.selected_tool.D3 /10
        self.scaled_values = {
            'D1': int((self.Parent.selected_tool.D1 * self.scale_width) / 2) / 100,
            'D2': int((self.Parent.selected_tool.D2 * self.scale_width) / 2) / 100 if self.Parent.selected_tool.D2 else int(((self.Parent.selected_tool.D1 - 0.2) * self.scale_width) / 2) / 100,
            'D3': int((self.Parent.selected_tool.D3 * self.scale_width) / 2) / 100,
            'L1': int(self.Parent.selected_tool.L1 * self.scale_width) / 100,
            'L2': int(self.Parent.selected_tool.L2 * self.scale_width) / 100 if self.Parent.selected_tool.L2 else int(self.Parent.selected_tool.L1 * self.scale_width) / 100,
            'L3': int(self.Parent.selected_tool.L3 * self.scale_width) / 100,
            'r': int(float(self.Parent.selected_tool.cornerRadius) * self.scale_width) / 100 if self.Parent.selected_tool.cornerRadius else 0,
        }

        self.center_of_rotation = self.scaled_values['L3'] / 2

        self.l2 = self.scaled_values["L2"] - self.scaled_values["L1"]
        self.l3 = self.scaled_values["L3"] - self.scaled_values["L2"] if self.scaled_values["L2"] else self.scaled_values["L3"] - self.scaled_values["L1"]

        glTranslatef(0, 0, -self.center_of_rotation)  # Move the object to the center of the screen

         
        self.units = self.parent.units


        
    def drawTool(self, picking=False):

        if picking:
            glDisable(GL_LIGHTING)
        else:
            self.setLighting()
            
            self.cutFaceColor = self.orange
            self.neckFaceColor = self.gray
            self.toolFaceColor = self.drakGray

        #check if the tool is selected and change the color
        if self.last_click3d == 16250871:
            self.holderFaceColor = self.blueShiny
        elif self.last_click3d == 32716:
            self.cutFaceColor = self.blueShiny
        elif self.last_click3d == 8355711:
            self.neckFaceColor = self.blueShiny
        elif self.last_click3d == 5000268:
            self.toolFaceColor = self.blueShiny

        # get tool type
        toolType = self.Parent.selected_tool.toolType

        neck = False

        # Draw the tool
        # cut
        if toolType == 1: # radius end mill
            #translate to the middle of the first cylinder
            #create face tip
            glTranslatef(0, 0, self.scaled_values["r"]/2)
            self.gl.DrawFaces(0, self.scaled_values["D1"] - self.scaled_values["r"], self.slices, self.cutFaceColor)
            #Torique cutting part
            self.gl.DrawTorique(self.scaled_values["D1"], self.scaled_values["r"], self.slices , self.cutFaceColor)
            self.gl.DrawCylinder(self.scaled_values["D1"], self.scaled_values["L1"] - self.scaled_values["r"], self.slices, self.cutFaceColor)
            
            neck = True

        elif toolType == 2: # spherical end mill

            # Translate to the middle of the first cylinder
            glTranslatef(0, 0, self.scaled_values["D1"])

            # Draw a sphere
            self.gl.DrawSphere(self.scaled_values["D1"], self.slices, self.cutFaceColor)

            # Draw a cylinder for the cutting part if it is greater than sphere radius
            if self.scaled_values["D1"] / 2 < self.scaled_values["L1"]:
                self.gl.DrawCylinder(self.scaled_values["D1"], self.scaled_values["L1"]  - (self.scaled_values["D1"]), self.slices, self.cutFaceColor)
                # Translate to the end of the cutting part
                #glTranslatef(0, 0, self.scaled_values["L1"]  - (self.scaled_values["D1"]))
                #self.gl.DrawCylinder(self.scaled_values["D1"], self.lineW, self.slices, self.black)
            neck = True

        elif toolType == 6:  # center drill
                        
            cone_height = ((self.Parent.selected_tool.D1/2) / math.tan(math.radians(self.Parent.selected_tool.neckAngle / 2)))
            #print(self.Parent.selected_tool.neckAngle, self.Parent.selected_tool.D1, cone_height)
            cone_height = cone_height * self.scale_width / 100
    
            self.gl.DrawCone(self.scaled_values["D1"], cone_height , self.slices, self.cutFaceColor)
                        
            self.gl.DrawCylinder(self.scaled_values["D1"], self.scaled_values["L1"] - cone_height , self.slices, self.cutFaceColor)

            if self.Parent.selected_tool.chamfer == '':
                chf = 60 
            else:
                chf = float(self.Parent.selected_tool.chamfer)           
            cone_height = (((self.Parent.selected_tool.D2-self.Parent.selected_tool.D1)/2) / math.tan(math.radians(chf/ 2)))

            #print((self.Parent.selected_tool.D2-self.Parent.selected_tool.D1)/2, self.Parent.selected_tool.chamfer, cone_height)
            cone_height = cone_height * self.scale_width / 100
            self.gl.DrawCone(self.scaled_values["D2"], cone_height, self.slices, self.cutFaceColor, self.scaled_values["D1"])
           
            self.gl.DrawCylinder(self.scaled_values["D2"], self.l2  - cone_height , self.slices, self.cutFaceColor)
   
            neck = False

        elif toolType == 7:  # drill
            # Draw the cone with the angle
            #need to scale the calcul with - self.Parent.selected_tool.neckAngle
            cone_height = self.scaled_values["D1"] / math.tan(math.radians(self.Parent.selected_tool.neckAngle/2))
            self.gl.DrawCone(self.scaled_values["D1"], cone_height, self.slices, self.cutFaceColor)
            # Draw the cylinder with the face color
            self.gl.DrawCylinder(self.scaled_values["D1"], self.scaled_values["L1"] - cone_height , self.slices, self.cutFaceColor)
            #glTranslatef(0, 0, self.scaled_values["L1"] - cone_height )
            # Draw the cylinder with the black color

            # Draw the neck part of the tool
            if self.l2 > 0:
                cone_height = 0                
                self.gl.DrawCylinder(self.scaled_values["D2"], self.l2 , self.slices, self.neckFaceColor)
                #glTranslatef(0, 0, self.l2 )
          
            neck = False

        else: # end mill

            # Draw the tip face
            self.gl.DrawFaces(0, self.scaled_values["D1"] , self.slices, self.cutFaceColor)
            # Draw the tip face contour
             # Draw the cylinder with the face color
            self.gl.DrawCylinder(self.scaled_values["D1"], self.scaled_values["L1"] , self.slices, self.cutFaceColor)
            # Translate to the end of the cut
            #glTranslatef(0, 0, self.scaled_values["L1"] )

            neck = True

        if neck:
            #glColor3ub(2, 0, 0)

            self.gl.DrawFaces(self.scaled_values["D2"] , self.scaled_values["D1"] , self.slices, self.neckFaceColor)
            # Draw the neck part of the tool
            self.gl.DrawCylinder(self.scaled_values["D2"], self.l2 , self.slices, self.neckFaceColor)
            # Draw the neck tip face
            self.gl.DrawFaces(self.scaled_values["D2"] , self.scaled_values["D3"] , self.slices, self.neckFaceColor)

        # Draw the main body of the tool
        self.gl.DrawCylinder(self.scaled_values["D3"], self.l3 , self.slices, self.toolFaceColor)
      
        # Draw the main body tip face
        self.gl.DrawFaces(0, self.scaled_values["D3"]  , self.slices, self.toolFaceColor)        


        if not picking:
            slider = self.parent.tool_slider.Value-self.parent.selected_tool.L3
            
            self.gl.displayToolHolder(slider, self.scale_width )
            
            glDisable(GL_LIGHTING)

            self.gl.draw_canvas3d(self, self.parent.selected_tool,self.scale_width, self.last_click3d)

            glTranslatef(0, 0, -self.scaled_values["L3"])
            
            self.gl.DrawCoordinateSystem(self, self.scaled_values["D1"] * 1.5)

            self.gl.DrawRule(self, self.Parent.selected_tool.L3, self.scaled_values["L3"], self.scaled_values["D3"], 1 * self.scale_width / 100,self.units)
       
            self.SwapBuffers()


    def DrawToolDetails(self, picking=False):
        if self.last_click3d not in [32716, 8355711, 5000268]:
            return

        if picking:
            # Usar cores de picking
            color = self.idToColor(10)
        else:
            color = (0.0, 0.0, 0.0)  # black

        # start parameters
        l1 = 0
        d1 = 0
        l3 = 0
        rd1 = 0
        rl1 = 0
        ty = 0
        d3 = self.scaled_values["D3"]

        if self.last_click3d == 32716:
            l1 = self.scaled_values["L1"]
            d1 = self.scaled_values["D1"]
            l3 = self.scaled_values["L3"]
            rd1 = self.parent.selected_tool.D1
            rl1 = self.parent.selected_tool.L1
            ty = 1
        elif self.last_click3d == 8355711:
            l1 = self.scaled_values["L2"]
            d1 = self.scaled_values["D2"]
            l3 = self.scaled_values["L3"]
            rd1 = self.parent.selected_tool.D2
            rl1 = self.parent.selected_tool.L2
            ty = 2
        elif self.last_click3d == 5000268:
            l1 = self.scaled_values["L3"]
            d1 = self.scaled_values["D3"]
            rd1 = self.parent.selected_tool.D3
            rl1 = self.parent.selected_tool.L3
            l3 = 0
            ty = 3

        rot = 0

        glRotatef(rot, 0, 1, 0)

        glTranslatef( ((d3)+(d3/4))+.2, ((d3)+(d3/4))+.2, ((l1/2)+(l1/4)+0.2))
        # Draw the details
        self.gl.drawText(10, 10, 10, color, 'D'+str(ty)+': '+str(rd1))
        glTranslatef(-0.1, -.1, -.1)
        self.gl.drawText(10, 10, 10, color, 'L'+str(ty)+': '+str(rl1))   
        #invert translation
        glTranslatef(-((d3)+(d3/4))-.1, -((d3)+(d3/4))-.1, -((l1/2)+(l1/4)+.1))
        #invert rotation
        glRotatef(-rot, 0, 1, 0)
        

    def colorToId(self, r, g, b):
        return int(r) + (int(g) << 8) + (int(b) << 16)

    def idToColor(self, obj_id):
        r = (obj_id & 0xFF) / 255.0
        g = ((obj_id >> 8) & 0xFF) / 255.0
        b = ((obj_id >> 16) & 0xFF) / 255.0
        return (r, g, b)

    def HandleClick(self, obj_id):
        if obj_id == 16250871:
            self.last_click3d = None
        if obj_id in [11, 12, 13, 21, 22, 23]:
            self.is_resizing = True
            if obj_id >= 20:
                # Flechas de comprimento
                self.resizing_type = 'L1'
                self.resizing_index = obj_id - 20
                print(f"Flecha de comprimento L{self.resizing_index} clicada!")
            else:
                # Flechas de diâmetro
                self.resizing_type = 'D1'
                self.resizing_index = obj_id - 10
                print(f"Flecha de diâmetro D{self.resizing_index} clicada!")
            self.is_resizing = True
            self.CaptureMouse()
            self.last_click3d = 0
        else:
            if obj_id in [32716, 8355711, 5000268]:
                self.last_click3d = obj_id
            print(f"Objeto clicado com ID: {obj_id}")
        

    def OnMouseMotion(self, event):
        #if self.last_click3d is not None:
        #    return

        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.GetPosition()
        
        current_pos = event.GetPosition()
        dx = current_pos.x - self.last_mouse_pos.x
        dy = current_pos.y - self.last_mouse_pos.y
        
        if self.is_resizing:
            delta = dy * 0.1  # Ajuste o fator de sensibilidade conforme necessário
            if self.resizing_type == 'D1':
                param_name = f'D1'
            elif self.resizing_type == 'L1':
                param_name = f'L1'
            
            current_value = getattr(self.Parent.selected_tool, param_name)
            new_value = max(0.0, current_value + delta)
            setattr(self.Parent.selected_tool, param_name, new_value)
            print(f"{param_name} atualizado para {new_value:.2f}")
            
            self.Refresh()
        else:
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

    def OnLeftClick(self, event):
        
        x, y = event.GetPosition()
        width, height = self.GetSize()
        y = height - y  # Ajusta a coordenada Y para o OpenGL
        # Renderiza a cena no modo de picking
        self.renderSceneForPicking()

        # Criar um buffer NumPy para armazenar os dados do pixel
        pixel = np.zeros((1, 1, 3), dtype=np.uint8)
        glReadBuffer(GL_BACK)
        glReadPixels(x, y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE, pixel)

        # Extrair os valores RGB corretos
        r = pixel[0][0][0]
        g = pixel[0][0][1]
        b = pixel[0][0][2]

        obj_id = self.colorToId(r, g, b)
        print(f"Objeto selecionado ID0: {obj_id}")

        self.HandleClick(obj_id)

    def OnMidDown(self, event):

        # add rotation
        self.is_rotating = True
        self.CaptureMouse()
        # redraw the scene
        self.Refresh()
        # call the click event        
        #self.OnLeftClick(event)

    def renderSceneForPicking(self):
        # render the scene for picking objects
        self.SetCurrent(self.context)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.setupScene()
        self.drawTool(picking=True)
        glFlush() 

    def OnMidUp(self, event):
        # stop resizing
        if self.is_resizing:
            self.is_resizing = False
            self.ReleaseMouse()
        # stop rotating
        if self.is_rotating:
            self.is_rotating = False
            self.ReleaseMouse()


    def OnRightDown(self, event):
        # start panning
        self.is_panning = True
        self.CaptureMouse()

    def OnRightUp(self, event):
        # stop panning
        if self.is_panning:
            self.is_panning = False
            self.ReleaseMouse()
        

    def OnSize(self, event):

        # get canvas size
        self.size = self.GetSize()
        
        ### print(self.size.width, self.size.height)  # Debug       

        self.SetCurrent(self.context)

        fov = 35.0  # view angle
        if self.size.height == 0 or self.size.width == 0:
            aspect_ratio = 1.0
        else:
            aspect_ratio = self.size.width / self.size.height  
        near_plane = 0.1  # zoom min
        far_plane = 1000.0  # zoom max

        glViewport(0, 0, self.size.width, self.size.height) # set the viewport

        glMatrixMode(GL_PROJECTION) # set the projection matrix
        glLoadIdentity() # reset the projection matrix
        gluPerspective(fov, aspect_ratio, near_plane, far_plane) # set the perspective
        glMatrixMode(GL_MODELVIEW) # set the modelview matrix
        glLoadIdentity() # reset the modelview matrix

    def OnTimer(self, event):
        self.Refresh()
    
    def OnMouseWheel(self, event):
        # add zoom
        delta = (event.GetWheelRotation() / event.GetWheelDelta())/3
        self.camera_distance -= delta
        if self.camera_distance < 1:
            self.camera_distance = 1  # zoom min
        if self.camera_distance > 50:
            self.camera_distance = 50  # zoom max
        self.Refresh()

    