#!/usr/bin/python
# -*-coding:utf-8-*-

"""
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions: 
* 
* The above notice and this permission notice shall be included in all copies
* or substantial portions of the Software.
* 
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*
* File for "Basic Shapes" lesson of the OpenGL tutorial on
* www.videotutorialsrock.com
*
* File in python created by Sehnoax based on files from 
* www.videotutorialsrock.com
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from wx import *
from wx.glcanvas import *

import math  


class myGLCanvas(GLCanvas):
    def __init__(self, parent):
        """
        Création du canevas recevant la modélisation 3D
        """
        #Initialisation du canevas
        GLCanvas.__init__(self, parent,-1)
        
        self.init = False
        self.context = GLContext(self)

        self.rotation_angle_x = 0.0
        self.rotation_angle_y = 0.0
        self.last_mouse_pos = None

        self.Bind(EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(EVT_MOTION, self.OnMouseMove)

        self.Bind(EVT_PAINT, self.OnPaint)
        self.Bind(EVT_SIZE, self.OnResize)
        self.Bind(EVT_KEY_DOWN, self.handleKeypress)
        

    def initRendering(self):
        """
        Initialisation du rendu
        """
        glEnable(GL_DEPTH_TEST)
        
    def OnLeftDown(self, event):
        self.CaptureMouse()
        self.last_mouse_pos = event.GetPosition()

    def OnLeftUp(self, event):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            mouse_pos = event.GetPosition()
            if self.last_mouse_pos:
                delta_x = mouse_pos.x - self.last_mouse_pos.x
                delta_y = mouse_pos.y - self.last_mouse_pos.y
                sensitivity = 0.5  # Adjust sensitivity as needed
                self.rotation_angle_x += delta_y * sensitivity
                self.rotation_angle_y += delta_x * sensitivity
                self.Refresh()
            self.last_mouse_pos = mouse_pos

    def OnPaint(self, event):
        """
        Fonction appeler pour dessiner les objets
        """
        # Si l'initialisation n'a pas été effectuée, on l'effectue
        # Initialisation du rendu effectuée ici car l'event PAINT appele cette
        # fonction avant que les fonctions situées dans l'init.
        # Permet d'optimiser le temps d'affichage surtout lors de l'utilisation
        # de texture.
        if not self.init:
            self.init = True
            self.SetCurrent(self.context)
            self.initRendering()

            # On force le redimensionnement de la fenêtre pour afficher les objets
            self.OnResize(0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Apply translation to move the cylinder to the center
        glTranslatef(0.0, 0.0, -2.0)  # Adjust the z-coordinate as needed
        
        # Apply rotations
        glRotatef(self.rotation_angle_x, 1, 0, 0)
        glRotatef(self.rotation_angle_y, 0, 1, 0)
        
        # Draw cylinders with different colors

        
        self.draw_cylinder(0.2, 0.4, 100, color=(1.0, 0.5, 0.0))  # Orange for tool
        glTranslatef(0.0, 0.0, .4)  # Adjust the z-coordinate as needed

        self.draw_cylinder(0.2, 1, 100, color=(0.5, 0.5, 0.5))  # Gray for cut neck
        self.draw_cylinder(0.2, 2, 100, color=(0.5, 0.5, 0.5))  # Gray for shank

        self.SwapBuffers()

  

    def OnResize(self, event):
        """
        Permet de dire à OpenGl comment convertir les coordonnées en valeurs
        pixel
        """
        if not self.init : return
        
        #On récupère la taille du canevas
        w, h = self.GetSize()

        glViewport(0, 0, w, h)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(45., \
                       float(w)/float(h), \
                       1., \
                       200.)

        self.OnPaint(-1) #Rafraichissement de la fenêtre pour forcer le OnPaint
        

    def handleKeypress(self, event):
        """
        Arrête programme si touche Echap enfoncée
        """
        key = event.GetUnicodeKey()
        if key == 27 : exit()
    
    def draw_cylinder(self, radius, height, slices=100, color=(0.5, 0.5, 0.5)):
        """
        Draws a cylinder with the specified radius, height, and color.
        """
        # Set color
        glColor3f(*color)  # Set color based on the provided tuple (r, g, b)

        glBegin(GL_QUAD_STRIP)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            # Bottom circle
            glVertex3f(x, y, 0)
            
            # Top circle
            glVertex3f(x, y, height)
        glEnd()

        # Apply texture, if needed

class test(wx.Frame):
    def __init__(self):
        """
        Initialisation de la frame utilisée pour afficher le canvas openGL
        """
        wx.Frame.__init__(self, None, \
                          title = "Basic Shapes - videotutorialsrock.com", \
                          size = (506, 432))
        aire = myGLCanvas(self)
        panel = wx.Panel(self, -1, size = (100, 432))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(aire, 1, wx.EXPAND)
        sizer.Add(panel, 0)
        
        self.SetSizer(sizer)

        self.Show()


if __name__ == '__main__' :
    app = wx.App()
    frame = test()
    frame.Show()
    app.MainLoop()
