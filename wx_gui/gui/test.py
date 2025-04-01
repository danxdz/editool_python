import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
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

        self.camera_distance = 10.0  # Distância da câmera (para zoom)
        self.camera_angle_x = 0  # Ângulo de rotação em torno do eixo X
        self.camera_angle_y = 0  # Ângulo de rotação em torno do eixo Y
        self.pan_x = 0  # Deslocamento de pan no eixo X
        self.pan_y = 0  # Deslocamento de pan no eixo Y

        self.last_mouse_pos = None  # Para armazenar a última posição do mouse

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
        glClearColor(1.0, 1.0, 1.0, 1.0)  # Fundo branco (RGBA)

    def OnPaint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Configurar a câmera com base no zoom, rotação e pan
        glTranslatef(self.pan_x, self.pan_y, -self.camera_distance)
        glRotatef(self.camera_angle_x, 1, 0, 0)
        glRotatef(self.camera_angle_y, 0, 1, 0)

        # Desenha dois cilindros
        self.DrawCylinder(1, 2, 32, (0, 0, 1))  # Cilindro azul
        glTranslatef(2, 0, 0)  # Mover um pouco para a direita
        self.DrawCylinder(0.5, 4, 32, (1, 0, 0))  # Cilindro vermelho

        self.SwapBuffers()

    def DrawCylinder(self, radius, height, slices, color):
        # Configura a cor do cilindro
        glColor3f(*color)

        # Desenha o cilindro
        quad = gluNewQuadric()
        glPushMatrix()
        glTranslatef(0, 0, -height / 2)  # Mover o cilindro para o centro
        gluCylinder(quad, radius, radius, height, slices, 1)
        glPopMatrix()

    def OnSize(self, event):
        size = self.GetClientSize()
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
        if self.camera_distance < 2:
            self.camera_distance = 2  # Limite mínimo de zoom
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

app = MyApp(False)
app.MainLoop()
