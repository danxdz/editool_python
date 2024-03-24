import wx
import open3d as o3d

class Open3DControl(wx.Window):
    def __init__(self, parent):
        super().__init__(parent)

        # Bind the render event to update the visualization
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        self.vis_window.update_renderer()


class Open3DMainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Open3D Visualization in wxPython", size=(200, 200))
        
        panel = wx.Panel(self, -1, size = (100, 432))
        
        # Create the Open3D control
        self.open3d_control = Open3DControl(self)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.open3d_control, 1, wx.EXPAND)
        sizer.Add(panel, 0)

        self.SetSizer(sizer)

        # Create Open3D visualization window
        self.vis_window = o3d.visualization.Visualizer()
        #change window size
        self.vis_window.create_window(width=400, height=400)

        mesh_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=0.3,height=8.0, resolution=200, split=30, create_uv_map=True)
        mesh_cylinder.paint_uniform_color([0.8, 0.6, 0.6])
  
        mesh_cylinder2 = o3d.geometry.TriangleMesh.create_cylinder(radius=0.3,height=4.0, resolution=200, split=30, create_uv_map=True)
        mesh_cylinder2.compute_vertex_normals()
        mesh_cylinder2.paint_uniform_color([0.5, 0.5, 0.5])

        mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.6, origin=[0,0,0])
     
        self.open3d_control.vis_window.add_geometry(mesh_cylinder)
        self.open3d_control.vis_window.add_geometry(mesh_cylinder2)
        self.open3d_control.vis_window.add_geometry(mesh_frame)
        self.open3d_control.vis_window.run()

        # Show the frame
        self.Show()
 

if __name__ == '__main__' :
    app = wx.App()
    frame = Open3DMainFrame()
    frame.Show()
    app.MainLoop()
