import numpy
 
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import ArrayDatatype
 
import wx
import wx.glcanvas
 
 
class MainFrame(wx.Frame):
    VERTEX_SHADER = """
        #version 150
 
        in vec3 vertex_position;
 
        void main() {
            gl_Position = vec4(vertex_position, 1.0);
        }
        """
 
    FRAGMENT_SHADER = """
        #version 150
 
        out vec4 frag_colour;
 
        void main() {
            frag_colour = vec4(0.0, 0.0, 1.0, 1.0);
        }
        """
 
    def __init__(self):
        wx.Frame.__init__(self, None, title="Hello World", size=(640, 480))
 
        self.points = numpy.array([[0.0, 0.5, 0.0],
                                   [0.5, -0.5, 0.0],
                                   [-0.5, -0.5, 0.0]], numpy.float32)
 
        self.initialized = False
        self.vbo = None
        self.program = None
 
        attributes = (wx.glcanvas.WX_GL_RGBA,
                      wx.glcanvas.WX_GL_DOUBLEBUFFER,
                      wx.glcanvas.WX_GL_DEPTH_SIZE, 24)
 
        self.canvas = wx.glcanvas.GLCanvas(self, attribList=attributes)
        self.context = wx.glcanvas.GLContext(self.canvas)
 
        self.canvas.Bind(wx.EVT_SIZE, self.on_size)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
 
    def init_opengl(self):
        self.initialized = True
 
        self.program = shaders.compileProgram(
            shaders.compileShader(MainFrame.VERTEX_SHADER, GL_VERTEX_SHADER),
            shaders.compileShader(MainFrame.FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )
 
        vertex_position_index = glGetAttribLocation(self.program, "vertex_position")
 
        self.vbo = glGenBuffers(1)
        # bind buffer to specific binding point
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # create data store for buffer
        glBufferData(GL_ARRAY_BUFFER,  # binding target
                     ArrayDatatype.arrayByteCount(self.points),  # size in bytes for new data store
                     ArrayDatatype.voidDataPointer(self.points),  # pointer to data that will be copied into data store
                     GL_STATIC_DRAW)  # usage
 
        # this binds the buffer to the attribute at the given location and
        # describes the format of the data in the buffer
        glVertexAttribPointer(vertex_position_index,
                              3,  # number of components per generic vertex attribute
                              GL_FLOAT,  # data type of each component in the array
                              GL_FALSE,  # are the data to be normalized?
                              0,  # byte offset between consecutive generic vertex attributes
                              None)  # offset of the first component of the first generic vertex attribute in the array
 
        # enable use of vertex buffer
        glEnableVertexAttribArray(vertex_position_index)
 
        # set background color to white
        glClearColor(1, 1, 1, 1)
 
    def draw(self):
        self.canvas.SetCurrent(self.context)
 
        glUseProgram(self.program)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, len(self.points))
 
        self.canvas.SwapBuffers()
 
    def on_size(self, event):
        self.canvas.SetCurrent(self.context)
 
        size = self.canvas.GetClientSize()
        glViewport(0, 0, size.width, size.height)
 
        self.canvas.Refresh(False)
 
    def on_paint(self, event):
        if not self.initialized:
            self.init_opengl()
 
        self.draw()
 
 
if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()