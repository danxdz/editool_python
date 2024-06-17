import wx
import open3d as o3d

class Open3DControl(wx.Window):
    def __init__(self, parent):
        super().__init__(parent)

        # Create Open3D visualization window
        self.vis_window = o3d.visualization.Visualizer()
        #change window size
        self.vis_window.create_window(width=400, height=200)
     
        mesh_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=0.3,height=8.0, resolution=200, split=30, create_uv_map=True)
        mesh_cylinder.paint_uniform_color([0.8, 0.2, 0.3])
  
        mesh_cylinder2 = o3d.geometry.TriangleMesh.create_cylinder(radius=0.3,height=4.0, resolution=200, split=30, create_uv_map=True)
        mesh_cylinder2.compute_vertex_normals()
        mesh_cylinder2.paint_uniform_color([0.5, 0.5, 0.5])

        mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.6, origin=[0,0,0])
     
        self.vis_window.add_geometry(mesh_cylinder)
        self.vis_window.add_geometry(mesh_cylinder2)
        self.vis_window.add_geometry(mesh_frame)
        self.vis_window.run()
        # Bind the render event to update the visualization
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        self.vis_window.update_renderer()

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Open3D Visualization in wxPython", size=(200, 200))

        panel = wx.Panel(self, -1, size = (100, 432))

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.open3d_control = None
        open3d_control = Open3DControl(self)

        # add the Open3D control to the sizer
        sizer.Add(open3d_control, 1, wx.EXPAND)
        sizer.Add(panel, 0)

        # add buttons to the panel
        button1 = wx.Button(panel, label="Button 1")
        button2 = wx.Button(panel, label="Button 2")
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(button1, 0, wx.EXPAND)
        sizer2.Add(button2, 0, wx.EXPAND)
        panel.SetSizer(sizer2)
        

        # Show the frame
        self.Show()

       

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()