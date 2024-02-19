import re



class CartesianPoint:
    def __init__(self, x, y, z):
        self.x = x/1000
        self.y = y/1000
        self.z = z/1000
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        return self.__str__()

class Direction:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        return self.__str__()

class Axis2Placement3D:
    def __init__(self, name, coord, dir_z, dir_x):
        self.name = name
        self.coord = coord
        self.dir_z = dir_z
        self.dir_x = dir_x
    
    def __str__(self):
        return f"{self.name}: coord={self.coord}, dir1={self.dir1}, dir2={self.dir2}"
    
    def __repr__(self):
        return self.__str__()
    
class ADVANCED_BREP_SHAPE_REPRESENTATION:
    def __init__(self, name, context_of_items, representation_identifier, representation_items):
        self.name = name
        self.context_of_items = context_of_items
        self.representation_identifier = representation_identifier
        self.representation_items = representation_items
    
    def __str__(self):
        return f"{self.name}: context_of_items={self.context_of_items}, representation_identifier={self.representation_identifier}, representation_items={self.representation_items}"
    
    def __repr__(self):
        return self.__str__()

    

class StepFileViewer:
    def __init__(self):
        self.step_data = None

    def loadStepFile(self, step_file_path):
        try:
            with open(step_file_path, 'r') as step_file:
                self.step_data = step_file.readlines()

        except Exception as e:
            print(f"Error loading STEP file: {e}")
            raise

    #def findPlacementElements(self, element_names):
    def findPlacementElements(self):
        found_elements = {}

        if self.step_data is None:
            print("Step data not loaded. Call loadStepFile() first.")
            return found_elements

        for line in self.step_data:
            if line.startswith("#"):
                # #1661=AXIS2_PLACEMENT_3D('MCS',#1658,#1659,#1660);
                # Break down the line into its parts
                parts = re.split(r'[(),]', line)
                try:
                    # Get the element number
                    num = parts[0].replace("#", "")
                    element_number = num.split("=")[0]
                    #remove leading and trailing spaces
                    element_type = num.split("=")[1].strip()
                    
                    #print(f"Element type: :{element_type}:")

                    # Check if the element type is AXIS2_PLACEMENT_3D:
                    if element_type == "AXIS2_PLACEMENT_3D":
                        # Get the element name
                        #print(f"Axis2Placement3D found: {element_number} {parts}")
                        element_name = parts[1].replace("'", "")

                        # Get the element content
                        element_content = parts[2:]

                        # If element has a name
                        if element_name:
                            # Use the element number as the name
                            #element_name = element_number
                            print(f"Named Axis2Placement3D found: {element_number} {parts}")


                        
                            cart = element_content[0].replace("#", "")
                            dir_z = element_content[1].replace("#", "")
                            dir_x = element_content[2].replace("#", "")

                            cart_content = self.get_element_content(cart)
                            dir_z_content = self.get_element_content(dir_z)
                            dir_x_content = self.get_element_content(dir_x)

                            coord = CartesianPoint(float(cart_content[0]), float(cart_content[1]), float(cart_content[2]))
                            dir_z = Direction(float(dir_z_content[0]), float(dir_z_content[1]), float(dir_z_content[2]))
                            dir_x = Direction(float(dir_x_content[0]), float(dir_x_content[1]), float(dir_x_content[2]))

                            axis_placement = Axis2Placement3D(element_name, coord, dir_z, dir_x)
                            found_elements[element_name] = axis_placement
                    if element_type == "ADVANCED_BREP_SHAPE_REPRESENTATION":
                        #example:
                        #11 = AXIS2_PLACEMENT_3D('',#12,#13,#14);
                        #12 = CARTESIAN_POINT('',(0.,0.,0.));
                        #13 = DIRECTION('',(0.,0.,1.));
                        #14 = DIRECTION('',(1.,0.,-0.));

                        #32 = ADVANCED_BREP_SHAPE_REPRESENTATION('',(#11,#33),#103);
                        #33 = MANIFOLD_SOLID_BREP('CUT',#34);
                        #34 = CLOSED_SHELL('',(#35,#69,#94));
                        #35 = ADVANCED_FACE('',(#36),#64,.F.);
                        #37 = EDGE_LOOP('',(#38,#49,#56,#57));
                        #38 = ORIENTED_EDGE('',*,*,#39,.F.);
                        #39 = EDGE_CURVE('',#40,#42,#44,.T.);
                        #40 = VERTEX_POINT('',#41);
                        #41 = CARTESIAN_POINT('',(2.999999999555,0.,-57.00000000508));
                        #42 = VERTEX_POINT('',#43);
                        #43 = CARTESIAN_POINT('',(-3.,0.,-57.));
                        #44 = CIRCLE('',#45,3.);
                        #45 = AXIS2_PLACEMENT_3D('',#46,#47,#48);
                        #46 = CARTESIAN_POINT('',(0.,0.,-57.));
                        #47 = DIRECTION('',(0.,0.,-1.));
                        #48 = DIRECTION('',(-1.,0.,0.));
                        #49 = ORIENTED_EDGE('',*,*,#50,.F.);
                        #50 = EDGE_CURVE('',#51,#40,#53,.T.);
                        #53 = B_SPLINE_CURVE_WITH_KNOTS('',1,(#54,#55),.UNSPECIFIED.,.F.,.F.,(2,2),(-1.564771298456E-15,3.01145951263),.PIECEWISE_BEZIER_KNOTS.);
                        #54 = CARTESIAN_POINT('',(0.,0.,-56.73753400942));
                        #55 = CARTESIAN_POINT('',(2.999999999555,7.347880793794E-16,-57.00000000508));
                        #56 = ORIENTED_EDGE('',*,*,#50,.T.);
                        #57 = ORIENTED_EDGE('',*,*,#58,.F.);
                        #58 = EDGE_CURVE('',#42,#40,#59,.T.);
                        #59 = CIRCLE('',#60,3.);
                        #60 = AXIS2_PLACEMENT_3D('',#61,#62,#63);
                        #61 = CARTESIAN_POINT('',(0.,0.,-57.));
                        #62 = DIRECTION('',(0.,0.,-1.));
                        #63 = DIRECTION('',(-1.,0.,0.));

                        #69 = ADVANCED_FACE('',(#70),#89,.T.);
                        #70 = FACE_BOUND('',#71,.T.);
                        #71 = EDGE_LOOP('',(#72,#81,#86,#87,#88));
                        #72 = ORIENTED_EDGE('',*,*,#73,.T.);
                        #73 = EDGE_CURVE('',#74,#74,#76,.T.);
                        #74 = VERTEX_POINT('',#75);
                        #75 = CARTESIAN_POINT('',(-2.997905604876,0.,-45.));
                        #76 = CIRCLE('',#77,2.997905604876);
                        #77 = AXIS2_PLACEMENT_3D('',#78,#79,#80);
                        #78 = CARTESIAN_POINT('',(0.,0.,-45.));
                        #79 = DIRECTION('',(0.,0.,-1.));
                        #80 = DIRECTION('',(-1.,0.,0.));
                        #81 = ORIENTED_EDGE('',*,*,#82,.T.);
                        #82 = EDGE_CURVE('',#74,#42,#83,.T.);
                        #83 = B_SPLINE_CURVE_WITH_KNOTS('',1,(#84,#85),.UNSPECIFIED.,.F.,.F.,(2,2),(-12.00000018277,0.),.PIECEWISE_BEZIER_KNOTS.);
                        #84 = CARTESIAN_POINT('',(-2.997905604879,-3.671375503161E-16,-45.));
                        #85 = CARTESIAN_POINT('',(-3.,-3.673940397442E-16,-57.));
                        #86 = ORIENTED_EDGE('',*,*,#39,.F.);
                        #87 = ORIENTED_EDGE('',*,*,#58,.F.);
                        #88 = ORIENTED_EDGE('',*,*,#82,.F.);
                        #89 = CONICAL_SURFACE('',#90,3.,1.745329250003E-04);
                        #90 = AXIS2_PLACEMENT_3D('',#91,#92,#93);
                        #91 = CARTESIAN_POINT('',(0.,0.,-57.));
                        #92 = DIRECTION('',(0.,0.,-1.));
                        #94 = ADVANCED_FACE('',(#95),#98,.F.);



                        # Get the element name
                        brep_name = parts[1].replace("'", "")
                        # Get the element content
                        brep_content = parts[2:]
                        print(f"Advanced Brep Shape Representation found: {brep_name} {brep_content}")


                        

                except Exception as e:
                   #print(f"Error parsing element content: {e}")
                    pass

        return found_elements

    def get_element_content(self, element_number):
        content = []
        for line in self.step_data:
            if line.startswith(f"#{element_number}"):
                parts = re.split(r'[(),]', line)
                try:
                    x = parts[3].replace("'", "")
                    y = parts[4].replace("'", "")
                    z = parts[5].replace("'", "")
                    content = [x, y, z]
                except Exception as e:
                    pass
                    #print(f"Error parsing element content: {e}")
        return content
