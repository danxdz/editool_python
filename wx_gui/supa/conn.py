import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math


# Inicializar o Firebase com as credenciais
cred = credentials.Certificate("G:\\works\\2023\\git clone\\editool_python\\wx_gui\\supa\\editool.json")
firebase_admin.initialize_app(cred)

# Criar o cliente Firestore
db = firestore.client()

db_name = 'players'

#check the number of documents in the collection
docs = db.collection(db_name).stream()
docs_len = len(list(docs))

#when connected to the database create a new document like P + number of documents in the collection
doc_ref = db.collection(db_name).document('p'+str(docs_len))
#set the initial coordinates to 0,Nb docs * 2
y = docs_len * 2
doc_ref.set({
    'coord': [0, y]
})


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
        self.pan_x = -0.8
        self.pan_y = -1.2
        self.last_mouse_pos = None

        self.x = 0
        self.y = 0

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

        self.camera_distance = 50  # Distância da câmera (para zoom)
        self.camera_angle_x = 0  # Ângulo de rotação em torno do eixo X
        self.camera_angle_y = 135 # Ângulo de rotação em torno do eixo Y

        self.listen_for_changes(db_name)

         # Função para escutar mudanças na coleção
    def listen_for_changes(self, collection_name):
        # Configurar o listener na coleção
        #doc_ref = db.collection(collection_name)
        #doc_ref.on_snapshot(self.on_snapshot)
        print('Listening for changes...')
            
    def on_snapshot(self, doc_snapshot, changes, read_time):
            for doc in doc_snapshot:
                if doc.exists:
                    data = doc.to_dict()
                    if 'coord' in data:
                        #self.x, self.y = data['coord']
                        print(f'Updated coordinates: x={self.x}, y={self.y} :: read_time={read_time}')
                else:
                    print(f'Document {doc.id} no longer exists.')


    def InitGL(self):
        # Configurações básicas de OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)  # Ativar anti-aliasing (suavização de bordas)
        glClearColor(0.9, .9, .9, 1)  # Fundo branco (RGBA)

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

        lineW = 0.08

        tool_max_width = 200
        tool_max_height = 100

        scale_width = (tool_max_width) / 200
        scaled_values = {
            'D1': 6,
            'D2':  5.8,
            'D3': 6,
            'L1': 5,
            'L2': 15,
            'L3': 50,
        }

        center_of_rotation = scaled_values['L3'] / 2
        
        lineW = (lineW * scale_width)/100
   
        l2 =  scaled_values["L2"] - scaled_values["L1"]
        l3 = scaled_values["L3"]-scaled_values["L2"]

        # get tool type
        toolType = 2

        # Draw the tool
        # cut
        if toolType == 2:
            glTranslatef(self.x, self.y, scaled_values["D1"]/2)
            self.DrawSphere(scaled_values["D1"], slices, cutFaceColor)
            #self.DrawCylinder(scaled_values["D1"], scaled_values["L1"]-lineW-(scaled_values["D1"]/2), slices, cutFaceColor)  
            self.DrawCylinder(scaled_values["D1"], scaled_values["L3"], slices, cutFaceColor)  
            glTranslatef(self.x, self.y, scaled_values["L1"]-lineW-(scaled_values["D1"]/2))  

        else:            
            # draw tip face
            self.DrawFaces(scaled_values["D1"], slices,  cutTipColor, lineW)
            # draw tip face contour        
            self.DrawContourFaces(scaled_values["D1"], slices,  cutContourColor, lineW)
            #draw the cylinder black
            self.DrawCylinder(scaled_values["D1"], lineW, slices, cutContourColor)
            glTranslatef(0, 0, lineW)
            #draw the cylinder with the face color
            self.DrawCylinder(scaled_values["D1"], scaled_values["L1"]-lineW, slices, cutFaceColor)  
            #translate to the end of the cut
            glTranslatef(0, 0, scaled_values["L1"]-lineW)  
    

            self.DrawCylinder(scaled_values["D1"], lineW, slices, cutContourColor)
            self.DrawFaces(scaled_values["D1"], slices,  cutTipColor, lineW)
            self.DrawContourFaces(scaled_values["D1"], slices,  cutContourColor, lineW)
            # noCut - neck
            self.DrawCylinder(scaled_values["D2"], l2, slices, neckFaceColor)
            # noCut - shank
            glTranslatef(0, 0, l2)  
            self.DrawCylinder(scaled_values["D3"], l3-lineW, slices, toolFaceColor)
            glTranslatef(0, 0, l3-lineW)
            self.DrawCylinder(scaled_values["D3"], lineW, slices, toolContourColor)
            glTranslatef(0, 0, lineW)
            self.DrawFaces(scaled_values["D3"], slices,  toolTipColor, lineW)
            self.DrawContourFaces(scaled_values["D3"], slices,  toolContourColor, lineW)

        #self.render_text("This is sample text", (25, 50), 1.2, (1, 0))
        #self.render_text("(C) LearnOpenGL.com", (50, 200), 0.9, (1, -0.25))

        self.SwapBuffers()

    def DrawSphere(self, radius, slices,color):
        # Configura a cor da esfera
        glColor3f(*color)
        # Desenha a esfera
        quad = gluNewQuadric()
        gluSphere(quad, radius, slices, slices)

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

    def DrawFaces(self, radius,slices, color,lineW):
        # Configura a cor do cilindro
        glColor3f(*color)
        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        gluDisk(quad, 0, radius-lineW, slices, 10)
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
        delta = event.GetWheelRotation() / event.GetWheelDelta()
        self.camera_distance -= delta
        if self.camera_distance < 0:
            self.camera_distance = 0  # Limite mínimo de zoom
        if self.camera_distance > 150:
            self.camera_distance = 150  # Limite máximo de zoom
        self.Refresh()

    def OnMouseMotion(self, event):
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.GetPosition()

        current_pos = event.GetPosition()
        dx = current_pos.x - self.last_mouse_pos.x
        dy = current_pos.y - self.last_mouse_pos.y
        print(f'dx={dx}, dy={dy}')

        if self.is_rotating:
            # Rotacionar a cena com o movimento do mouse
            self.camera_angle_x += dy * 0.5
            self.camera_angle_y += dx * 0.5
        elif self.is_panning:
            # Pan com movimento do mouse
            #check if the movement is greater than 0.1
            #if it is update the coordinates
            self.x += dx * -0.1
            self.y -= dy * 0.1
            print(f'x={self.x}, y={self.y}')
            if dx * 0.1 > self.x + 0.1 or dy * 0.1 > self.y + 0.1 or dx * 0.1 < self.x - 0.1 or dy * 0.1 < self.y - 0.1:                
                #update the coordinates in the database
                doc_ref.update({
                    'coord': [self.x, self.y]   
                })
                #self.pan_x += dx * 0.01
                #self.pan_y -= dy * 0.01

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

    def makefont(self, filename, fontsize):
        
        face = Face(filename)
        face.set_pixel_sizes( 0, fontsize )
 
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glActiveTexture(GL_TEXTURE0)

        for c in range(128):
            #face.load_char( chr(c), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT )
            face.load_char( chr(c), FT_LOAD_RENDER )
            glyph   = face.glyph
            bitmap  = glyph.bitmap
            size    = bitmap.width, bitmap.rows
            bearing = glyph.bitmap_left, glyph.bitmap_top 
            advance = glyph.advance.x

            # create glyph texture
            texObj = glGenTextures(1)
            glBindTexture( GL_TEXTURE_2D, texObj )
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
            #databuffer = numpy.zeros((cx, width*16), dtype=numpy.ubyte)
            glTexImage2D( GL_TEXTURE_2D, 0, GL_R8, *size, 0, GL_RED, GL_UNSIGNED_BYTE, bitmap.buffer )

            self.characters.append((texObj, size, bearing, advance))

        glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
        glBindTexture(GL_TEXTURE_2D, 0)

    def render_text(self, text, pos, scale, dir):
        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.vao)
        angle_rad    = math.atan2(dir[1], dir[0])
        rotateM      = glm.rotate(glm.mat4(1), angle_rad, glm.vec3(0, 0, 1))
        transOriginM = glm.translate(glm.mat4(1), glm.vec3(*pos, 0))

        char_x = 0
        for c in text:
            c = ord(c)
            ch          = self.characters[c]
            w, h        = ch[1][0] * scale, ch[1][1] * scale
            xrel, yrel  = char_x + ch[2][0] * scale, (ch[1][1] - ch[2][1]) * scale
            char_x     += (ch[3] >> 6) * scale 
            scaleM      = glm.scale(glm.mat4(1), glm.vec3(w, h, 1))
            transRelM   = glm.translate(glm.mat4(1), glm.vec3(xrel, yrel, 0))
            modelM      = transOriginM * rotateM * transRelM * scaleM
            
            glUniformMatrix4fv(0, 1, GL_FALSE, glm.value_ptr(modelM))
            glBindTexture(GL_TEXTURE_2D, ch[0])
            glDrawArrays(GL_TRIANGLES, 0, 6)

        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
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
    
app = MyApp()
app.MainLoop()

#when the application is closed delete the document
doc_ref.delete()

