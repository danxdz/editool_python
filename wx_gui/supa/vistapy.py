from netgen.occ import OCCGeometry, Glue
from ngsolve import Mesh, VTKOutput
import pyvista as pv

geo = OCCGeometry("G:\\works\\2023\\git clone\\editool_python\\wx_gui\\supa\\Seco_02752981_LWT.stp")
#geo = OCCGeometry("G:\\works\\2023\\git clone\\editool_python\\wx_gui\\supa\\CAD_122635_6.stp")
shape2 = geo.shape

for f in shape2.faces:
    print(f.name)
    
partgeo = OCCGeometry(shape2)

mesh = Mesh(partgeo.GenerateMesh(maxh=0.5))

vtk = VTKOutput(ma=mesh,filename="Face3")
vtk.Do()


grid = pv.read("Face3.vtu")
plotter = pv.Plotter()
plotter.add_mesh(grid, opacity=1, interpolate_before_map=True,render=True)
plotter.enable_anti_aliasing("fxaa")
plotter.show()