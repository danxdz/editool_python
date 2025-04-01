import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutInit

class GameCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        attribList = [
            glcanvas.WX_GL_RGBA,
            glcanvas.WX_GL_DOUBLEBUFFER,
            glcanvas.WX_GL_DEPTH_SIZE, 16,
            glcanvas.WX_GL_SAMPLE_BUFFERS, 1,
            glcanvas.WX_GL_SAMPLES, 4,
            0
        ]
        super().__init__(parent, -1, attribList=attribList)
        self.context = glcanvas.GLContext(self)
        self.init = False
        self.size = self.GetClientSize()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Eventos do mouse para controle da câmera
        self.Bind(wx.EVT_MIDDLE_DOWN, self.OnMiddleDown)
        self.Bind(wx.EVT_MIDDLE_UP, self.OnMiddleUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

        self.last_mouse_pos = None
        self.camera_distance = 5.0
        self.camera_angle_x = 0.0
        self.camera_angle_y = 0.0
        self.is_rotating = False

    def OnEraseBackground(self, event):
        pass  # Evita flickering

    def OnSize(self, event):
        self.size = self.GetClientSize()
        if self.IsShown():
            self.SetCurrent(self.context)
            glViewport(0, 0, self.size.width, self.size.height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(
                45.0,
                float(self.size.width) / float(self.size.height),
                0.1,
                100.0
            )
            glMatrixMode(GL_MODELVIEW)

    def OnPaint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()
        event.Skip()

    def InitGL(self):
        glutInit()
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)  # Anti-aliasing
        glShadeModel(GL_SMOOTH)   # Shading suave
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # Configurar iluminação
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

        # Ativar névoa (fog)
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_COLOR, [0.5, 0.5, 0.5, 1.0])
        glFogf(GL_FOG_DENSITY, 0.35)
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        glFogf(GL_FOG_START, 1.0)
        glFogf(GL_FOG_END, 10.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(
            45.0,
            float(self.size.width) / float(self.size.height),
            0.1,
            100.0
        )
        glMatrixMode(GL_MODELVIEW)

    def OnDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_angle_x, 1, 0, 0)
        glRotatef(self.camera_angle_y, 0, 1, 0)
        self.drawCube()
        self.SwapBuffers()

    def drawCube(self):
        glBegin(GL_QUADS)
        # Face frontal (vermelha)
        glColor3f(1.0, 0.0, 0.0)
        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        glVertex3f(1.0, -1.0,  1.0)
        glVertex3f(1.0, 1.0,  1.0)
        glVertex3f(-1.0, 1.0,  1.0)
        # Face traseira (verde)
        glColor3f(0.0, 1.0, 0.0)
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)
        # Face superior (azul)
        glColor3f(0.0, 0.0, 1.0)
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0,  1.0)
        glVertex3f(1.0, 1.0,  1.0)
        glVertex3f(1.0, 1.0, -1.0)
        # Face inferior (amarela)
        glColor3f(1.0, 1.0, 0.0)
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0,  1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        # Face direita (magenta)
        glColor3f(1.0, 0.0, 1.0)
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0,  1.0)
        glVertex3f(1.0, -1.0,  1.0)
        # Face esquerda (ciano)
        glColor3f(0.0, 1.0, 1.0)
        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        glVertex3f(-1.0, 1.0,  1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glEnd()

    def OnMiddleDown(self, event):
        self.is_rotating = True
        self.last_mouse_pos = event.GetPosition()
        self.CaptureMouse()

    def OnMiddleUp(self, event):
        self.is_rotating = False
        self.ReleaseMouse()

    def OnMouseMotion(self, event):
        if self.is_rotating:
            new_mouse_pos = event.GetPosition()
            dx = new_mouse_pos.x - self.last_mouse_pos.x
            dy = new_mouse_pos.y - self.last_mouse_pos.y
            self.camera_angle_x += dy * 0.5
            self.camera_angle_y += dx * 0.5
            self.last_mouse_pos = new_mouse_pos
            self.Refresh()

    def OnMouseWheel(self, event):
        rotation = event.GetWheelRotation()
        delta = -rotation / 120 * 0.5  # Ajuste a sensibilidade do zoom
        self.camera_distance += delta
        self.camera_distance = max(2.0, min(self.camera_distance, 20.0))  # Limitar distância da câmera
        self.Refresh()

class GameFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Game", size=(800, 600))
        self.canvas = GameCanvas(self)
        self.Show(True)

if __name__ == '__main__':
    app = wx.App()
    frame = GameFrame(None)
    app.MainLoop()