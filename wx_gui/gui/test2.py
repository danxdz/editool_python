import wx
from wx.glcanvas import GLCanvas, GLContext
from OpenGL.GL import *
from OpenGL.GLUT import glutInit, glutInitDisplayMode, glutInitWindowSize, glutSolidSphere, GLUT_RGB, GLUT_DOUBLE, GLUT_DEPTH
from OpenGL.GLUT import *
import ctypes
import sys
import os

class SphereCanvas(GLCanvas):
    def __init__(self, parent):
        super().__init__(parent)
        self.context = GLContext(self)
        self.init = False

        # Manually load freeglut.dll
        if sys.platform.startswith('win'):
            dll_name = 'freeglut.dll'
            dll_path = os.path.join(os.getcwd(), dll_name)
            if not os.path.exists(dll_path):
                # Try to locate the DLL in the script directory
                dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dll_name)
            if os.path.exists(dll_path):
                ctypes.WinDLL(dll_path)
            else:
                raise FileNotFoundError(f"{dll_name} not found. Ensure it is in the current directory.")

        glutInit(sys.argv)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def InitGL(self):
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)

    def OnPaint(self, event):
        # Required for Windows
        if not self.IsShown():
            return
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()
        self.SwapBuffers()

    def OnSize(self, event):
        width, height = self.GetClientSize()
        if self.context:
            self.SetCurrent(self.context)
            glViewport(0, 0, width, height)
        event.Skip()

    def OnDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        #create the window glut
        glutInit( [ ] )
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(800, 600)
       

        
        # Position the camera
        glTranslatef(0.0, 0.0, -5.0)
        glColor3f(0.0, 1.0, 0.0)
        # Draw the sphere using GLUT
        glutSolidSphere(1.0, 32, 32)
        


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='GLUT Sphere Example')
        self.canvas = SphereCanvas(self)
        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()