import sys
import os
import numpy as np
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopLoc import TopLoc_Location
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Global variables for storing vertices and indices
vertices = []
indices = []
angle_x = 0.0
angle_y = 0.0
zoom = 1.0
mouse_down = False
mouse_x = 0
mouse_y = 0
def read_step_file_geometry(step_file_path):
    # Read the STEP file using pythonocc-core
    reader = STEPControl_Reader()
    status = reader.ReadFile(step_file_path)
    if status != IFSelect_RetDone:
        print("Erro ao ler o arquivo STEP.")
        sys.exit(1)

    reader.TransferRoot()
    shape = reader.OneShape()

    # Generate mesh with a defined deflection
    linear_deflection = 0.1  # Adjust as needed
    angular_deflection = 0.5
    BRepMesh_IncrementalMesh(shape, linear_deflection, False, angular_deflection)

    # Explore geometry to extract faces
    exp = TopologyExplorer(shape)
    index_offset = 0

    global vertices, indices

    for face in exp.faces():
        # Get the location of the face
        location = TopLoc_Location()
        
        # Get the triangulation of the face
        triangulation = BRep_Tool.Triangulation(face, location)
        if triangulation is None:
            continue

        # Apply the location transformation
        trsf = location.Transformation()

        # Get the number of nodes and triangles
        num_nodes = triangulation.NbNodes()
        num_triangles = triangulation.NbTriangles()

        # Add vertices
        for i in range(1, num_nodes + 1):
            pnt = triangulation.Node(i)
            pnt.Transform(trsf)  # Transform the point
            vertices.extend([pnt.X(), pnt.Y(), pnt.Z()])

        # Add indices
        for i in range(1, num_triangles + 1):
            tri = triangulation.Triangle(i)
            n1, n2, n3 = tri.Get()
            # Subtract 1 because OpenGL uses zero-based indexing
            indices.extend([n1 - 1 + index_offset, n2 - 1 + index_offset, n3 - 1 + index_offset])

        index_offset += num_nodes



def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -50.0)
    # Apply zoom and rotations
    glScalef(zoom, zoom, zoom)
    glRotatef(angle_x, 1.0, 0.0, 0.0)
    glRotatef(angle_y, 0.0, 1.0, 0.0)
    glColor3f(0.8, 0.8, 0.8)
    glEnableClientState(GL_VERTEX_ARRAY)
    vertex_array = np.array(vertices, dtype=np.float32)
    index_array = np.array(indices, dtype=np.uint32)
    glVertexPointer(3, GL_FLOAT, 0, vertex_array)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, index_array)
    glDisableClientState(GL_VERTEX_ARRAY)
    glutSwapBuffers()

def mouse(button, state, x, y):
    global mouse_down, mouse_x, mouse_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_down = True
            mouse_x, mouse_y = x, y
        elif state == GLUT_UP:
            mouse_down = False

def motion(x, y):
    global angle_x, angle_y, mouse_x, mouse_y
    if mouse_down:
        dx = x - mouse_x
        dy = y - mouse_y
        angle_x += dy * 0.2
        angle_y += dx * 0.2
        mouse_x, mouse_y = x, y
        glutPostRedisplay()

def keyboard(key, x, y):
    global zoom
    if key == b'+':
        zoom *= 1.1
        glutPostRedisplay()
    elif key == b'-':
        zoom /= 1.1
        glutPostRedisplay()

def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.7, 0.7, 0.7, 1.0)
    glShadeModel(GL_SMOOTH)

def reshape(width, height):
    if height == 0:
        height = 1
    aspect = width / float(height)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, aspect, 1.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Adjust the camera position to better view the model
    gluLookAt(
        0, 0, 5000,  # Move the camera further back along Z-axis
        0, 0, 0,    # Look at the origin
        0, 1, 0     # Up vector
    )

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Visualizador de Arquivo STEP")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    init()
    glutMainLoop()

if __name__ == "__main__":
    local_path = os.path.dirname(os.path.realpath(__file__))
    step_file = os.path.join(local_path, 'cube2.stp')  # Replace with your STEP file

    read_step_file_geometry(step_file)

    # Check if vertices and indices are populated
    print(f"Number of vertices: {len(vertices) // 3}")
    print(f"Number of indices: {len(indices)}")

    main()