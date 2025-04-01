import firebase_admin
from firebase_admin import credentials, db
import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import hashlib
import json
import time
import vtk
from vtk import vtkOCCTReader
# Initialize Firebase with credentials
cred = credentials.Certificate("G:\\works\\2023\\git clone\\editool_python\\wx_gui\\supa\\editool.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://editool-c1806-default-rtdb.europe-west1.firebasedatabase.app/'
})

Reader = vtk.vtkCONVERGECFDReader()



ref = db.reference('/')  # Root of your database

db_name = 'players'

data = ref.get(db_name)
print(data)

# Function to calculate the checksum of the coordinates
def calculate_checksum(coords):
    coords_str = json.dumps(coords)
    return hashlib.sha256(coords_str.encode()).hexdigest()

# Initial checksum empty
initial_checksum = None

new_user_ref = ref.child('players').push()

docs_len = 1

# Define initial coordinates at [0, docs_len * 2]
y = docs_len * 2
initial_coords = [0, y]
initial_checksum = calculate_checksum(initial_coords)  # Calculate the initial checksum

# Create the document in Firestore with coordinates and checksum
new_user_ref.set({
    'coord': initial_coords,
    'checksum': initial_checksum  # Store the initial checksum
})

# Class that manages OpenGL rendering and player events
class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        attribs = [
            glcanvas.WX_GL_RGBA,
            glcanvas.WX_GL_DOUBLEBUFFER,
            glcanvas.WX_GL_DEPTH_SIZE, 24,
            glcanvas.WX_GL_SAMPLES, 4  # Enable anti-aliasing
        ]
        super(OpenGLCanvas, self).__init__(parent, attribList=attribs)
        self.context = glcanvas.GLContext(self)
        self.init = False
        self.pan_x = -0.8
        self.pan_y = -1.2
        self.last_mouse_pos = None
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.last_update_time = time.time()

        # Mouse events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)  # For zoom
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)     # For rotation and pan
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)     # To activate rotation
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)         # To deactivate rotation
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)   # To activate pan
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       # To deactivate pan

        self.timer = wx.Timer(self)
        self.timer.Start(16)  # Update the screen every 16 ms (~60 FPS)

        self.is_rotating = False
        self.is_panning = False

        self.camera_distance = 50  # Camera distance (for zoom)
        self.camera_angle_x = 0  # Rotation angle around the X axis
        self.camera_angle_y = 135  # Rotation angle around the Y axis

        # Set up the listener for changes in the Firestore collection
        self.listen_for_changes("players")

    def listen_for_changes(self, collection_name):
        # Configure the listener on the collection
        doc_ref = ref.child(collection_name)
        doc_ref.listen(self.on_snapshot)

    def on_snapshot(self, event):
        data = event.data
        if data:
            if 'coord' in data:
                self.target_x, self.target_y = data['coord']
                self.last_update_time = time.time()
                print(f'Updated coordinates: x={self.target_x}, y={self.target_y}')

    def InitGL(self):
        # Basic OpenGL settings
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)  # Enable anti-aliasing (edge smoothing)
        glClearColor(0.9, 0.9, 0.9, 1)  # White background (RGBA)

    def OnPaint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Pan
        glTranslatef(self.x, self.y, -self.camera_distance)
        # Orbiting
        glRotatef(self.camera_angle_x, 1, 0, 0)
        glRotatef(self.camera_angle_y, 0, 1, 0)

        # Interpolate between current position and target position
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        interpolation_factor = min(elapsed_time * 1, 1)  # Adjust the factor for smoothness

        self.x += (self.target_x - self.x) * interpolation_factor
        self.y += (self.target_y - self.y) * interpolation_factor

        # Example of rendering a sphere (symbolizing a player or object)
        self.DrawSphere(1, 20, (1, 0, 0))  # Draw a red sphere
        self.SwapBuffers()

    def DrawSphere(self, radius, slices, color):
        glColor3f(*color)
        quad = gluNewQuadric()
        gluSphere(quad, radius, slices, slices)

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
        self.Refresh()  # Constantly update the screen

    def OnMouseWheel(self, event):
        delta = event.GetWheelRotation() / event.GetWheelDelta()
        self.camera_distance -= delta
        if self.camera_distance < 0:
            self.camera_distance = 0
        if self.camera_distance > 150:
            self.camera_distance = 150
        self.Refresh()

    def OnMouseMotion(self, event):
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.GetPosition()

        current_pos = event.GetPosition()
        dx = current_pos.x - self.last_mouse_pos.x
        dy = current_pos.y - self.last_mouse_pos.y

        if self.is_rotating:
            self.camera_angle_x += dy * 0.5
            self.camera_angle_y += dx * 0.5
        elif self.is_panning:
            self.x += dx * 0.1
            self.y -= dy * 0.1
            # Update Firestore with coordinates and checksum
            new_coords = [self.x, self.y]
            new_checksum = calculate_checksum(new_coords)
            new_user_ref.update({
                'coord': new_coords,
                'checksum': new_checksum
            })

        self.last_mouse_pos = current_pos
        self.Refresh()

    def OnLeftDown(self, event):
        self.is_rotating = True
        self.CaptureMouse()

    def OnLeftUp(self, event):
        if self.is_rotating:
            self.is_rotating = False
            self.ReleaseMouse()

    def OnRightDown(self, event):
        self.is_panning = True
        self.CaptureMouse()

    def OnRightUp(self, event):
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

app = MyApp()
app.MainLoop()

# When the application is closed, delete the document in Firestore
new_user_ref.delete()