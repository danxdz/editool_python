import re

class named_frames:
    MCS = None
    CWS = None
    PCS = None
    WCS = None
    CSW = None

class CartesianPoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
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
    def __init__(self, name, coord, dir1, dir2):
        self.name = name
        self.coord = coord
        self.dir1 = dir1
        self.dir2 = dir2
    
    def __str__(self):
        return f"{self.name}: coord={self.coord}, dir1={self.dir1}, dir2={self.dir2}"
    
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

    def findPlacementElements(self, element_names):
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
                    element_type = num.split("=")[1]

                    # Check if the element type is AXIS2_PLACEMENT_3D:
                    if element_type == "AXIS2_PLACEMENT_3D":
                        # Get the element name
                        element_name = parts[1].replace("'", "")

                        # Get the element content
                        element_content = parts[2:]

                        # If element has a name
                        if True:#element_name:# and element_name in element_names:
                            cart = element_content[0].replace("#", "")
                            dir1 = element_content[1].replace("#", "")
                            dir2 = element_content[2].replace("#", "")

                            cart_content = self.get_element_content(cart)
                            dir1_content = self.get_element_content(dir1)
                            dir2_content = self.get_element_content(dir2)

                            coord = CartesianPoint(float(cart_content[0]), float(cart_content[1]), float(cart_content[2]))
                            dir1 = Direction(float(dir1_content[0]), float(dir1_content[1]), float(dir1_content[2]))
                            dir2 = Direction(float(dir2_content[0]), float(dir2_content[1]), float(dir2_content[2]))

                            axis_placement = Axis2Placement3D(element_name, coord, dir1, dir2)
                            found_elements[element_name] = axis_placement

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
