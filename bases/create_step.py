from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone

def create_step_cube(filename="cube.step"):
    # Create a cube with dimensions 10x10x10
    cube = BRepPrimAPI_MakeBox(5.0, 10.0, 10.0).Shape()
    # Create a cilinder with dimensions 10x10x10
    cilinder = BRepPrimAPI_MakeCylinder(1.0, 2.0).Shape()


    # Initialize STEP writer
    step_writer = STEPControl_Writer()
    step_writer.Transfer(cilinder, STEPControl_AsIs)
    step_writer.Transfer(cube, STEPControl_AsIs)

    # Write to file
    status = step_writer.Write(filename)
    if status == IFSelect_RetDone:
        print(f"STEP file '{filename}' successfully written!")
    else:
        print(f"Failed to write STEP file '{filename}'.")

# Call the function to create the STEP file
create_step_cube("valid_cube.step")
