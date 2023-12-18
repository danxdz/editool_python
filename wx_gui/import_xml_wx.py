import wx
import xml.etree.ElementTree as ET

from tool import Tool

from databaseTools import saveTool
from databaseTools import load_tools_from_database

def parse_hyper_xml_data(root):
    print("Parse Hyper xml data")
    
    # Obtém os dados da ferramenta
    tool = root.find('.//tool')
    #dbout("TOOL",tool)
    # Find the tecset with type="milling"
    milling_tecset = tool.find(".//tecset")

    # Extract the value of the 'coolants' parameter from the milling_tecset
    coolants_value = milling_tecset.find(
        ".//param[@name='coolants']").attrib['value']
    #print("Coolants value: ", coolants_value)

    #print(tool.attrib['name'])
    toolType = 0
    print("Tool type: ", toolType)

    if tool.attrib['type'] == "Tslotcutter":
        toolType = "tslotMill"
    else:
        toolType == tool.attrib['type']
    print("Tool type: ", toolType)

    tool_data = {
        # Adicione essa linha para obter o atributo 'name' do XML
        'Name': tool.attrib['name'],
        'toolType': toolType,
        'GroupeMat': tool.find('param[@name="cuttingMaterial"]').attrib['value'],
        'D1': float(tool.find('param[@name="toolDiameter"]').attrib['value']),
        'D2': float(tool.find('param[@name="toolDiameter"]').attrib['value'])-0.2,
        'D3': float(tool.find('param[@name="toolShaftDiameter"]').attrib['value']),
        'L1': float(tool.find('param[@name="cuttingLength"]').attrib['value']),
        'L2': float(tool.find('param[@name="taperHeight"]').attrib['value']),
        'L3': float(tool.find('param[@name="toolTotalLength"]').attrib['value']),
        'NoTT': int(tool.find('param[@name="cuttingEdges"]').attrib['value']),
        'RayonBout': float(tool.find('param[@name="cornerRadius"]').attrib['value']),
        'Chanfrein': tool.find('param[@name="toolShaftChamferAbsPos"]').attrib['value'],
        'CoupeCentre': "no",
        'ArrCentre': coolants_value,
        'threadPitch': "",
        'threadPitch': "threadPitch",
        'Manuf': tool.find('param[@name="manufacturer"]').attrib['value'],
        'ManufRef': tool.find('param[@name="orderingCode"]').attrib['value'],
        'ManufRefSec': tool.find('param[@name="comment"]').attrib['value'],
        'Code': " ",
        'CodeBar': tool.find('param[@name="orderingCode"]').attrib['value'],
        'Comment': tool.find('param[@name="comment"]').attrib['value'],
    }


    print("Tool :: ", tool_data)
    return Tool(**tool_data)



def get_property_value(tool, prop_name, default_value=''):
    properties = tool.findall(".//Property-Data")
    for prop in properties:
        prop_name_elem = prop.find("PropertyName[@source='din_mk']")
        if prop_name_elem is not None and prop_name_elem.text == prop_name:
            value_elem = prop.find("Value")
            value = value_elem.text.strip()
            value = value.replace(',', '.')
            if value_elem is not None and value:
                try:
                    return float(value)
                except ValueError:
                    return value
    return default_value


def check_fraisa_types(tool_id):
    # Sources from FRAISA.com
    radius_mill = [8107, 8720, 15502, 15572, 15573, 15574, 15575, 15582, 15583, 15584, 15585, 8507, 6032, 6034, 6036, 6038, 6040, 6042, 6044, 7284, 7288, 7340, 7344, 7620, 7624, 15268, 5257, 45319, 500022, 500023, 500024, 500025, 500046, 500047, 500048, 500049, 500050, 500051, 500052, 500053, 500054, 500055, 500056, 500057, 500058, 500059, 500060, 500061, 500062, 500063, 500064, 500065, 500066, 500067, 500068, 500069, 500070, 500071, 500072, 500073, 500074, 500075, 500076, 500077, 500085, 500086, 8617, 8117, 5234, 5250, 5252, 5640, 5645, 5650, 5752, 5754, 5756, 5762, 5764, 6531, 6532, 6533, 6534, 6535, 6536, 6538, 6735, 6736, 6738, 6740, 6742, 6744, 7100, 7104, 7200, 7204, 7600, 7604, 7608, 15226, 31410, 31420, 35400, 95752, 95754, 95756, 7210, 15512, 7610, 7612, 7614, 7212, 6816, 6818, 6820, 6823]
    ball_mill = [6062, 6064, 6066, 6068, 6070, 6072, 6074, 7400, 7404, 7408, 7460, 7464, 7484, 7488, 7500, 7540, 7544, 7550, 7402, 7554, 5286, 5288, 5289, 5580, 5782, 5784, 5786, 5787, 5791, 5792, 5793, 5794, 5796, 6460, 6461, 6462, 6463, 6464, 6481, 6482, 6483, 6560, 6561, 6562, 6563, 6564, 6565, 6566, 6567, 6568, 6579, 6581, 6582, 6583, 6765, 6766, 6768, 6770, 6772, 6774, 7450, 7454, 7458, 7470, 7474, 7478, 15781, 15795, 31700, 35700, 45298, 45785, 95782, 95784, 95786, 95787, 95791, 95793, 915795, 7472, 7490, 7492, 7494, 6832, 6836, 6840, 6844, 6846, 6847, 6848, 6849]
    end_mill = [500043, 500042, 500041, 500040, 500015, 500014, 500013, 500012, 500011, 500010, 500009, 500008, 500007, 500006, 500005, 500004, 500003, 500002, 500001, 500000, 95717, 95716, 95714, 95712, 46310, 46300, 45713, 45710, 45709, 45372, 45371, 45362, 45360, 45355, 45336, 45334, 45333, 45326, 45325, 45323, 45322, 45317, 20030, 20025, 20020, 15754, 15752, 15725, 15711, 15607, 15606, 15590, 15589, 15561, 15560, 15559, 15557, 15550, 15535, 15530, 15525, 15520, 15510, 15507, 15506, 15505, 15500, 15359, 15299, 15298, 15297, 15260, 15254, 15251, 15250, 15248, 15242, 15239, 15238, 15236, 15233, 15232, 15225, 15223, 15222, 15210, 15208, 15207, 8805, 8800, 8618, 8616, 8614, 8608, 8606, 8604, 8521, 8502, 8500, 8404, 8323, 8321, 8320, 8315, 8313, 8311, 8310, 8305, 8303, 8302, 8301, 8300, 8121, 8115, 8112, 8111, 8105, 8102, 8101, 8100, 6812, 6811, 6810, 6809, 6807, 6804, 6802, 6800, 6508, 6506, 6505, 6504, 6503, 6502, 6501, 6500, 5724, 5723, 5722, 5721, 5717, 5716, 5714, 5712, 5400, 5336, 5335, 5329, 5297, 5279, 5272, 5255, 5249, 5237, 5225, 5219, 5218, 5215, 5214, 5213, 5200, 5036, 780, 700, 695, 665, 659, 650, 621, 619, 610, 609, 540, 410, 400, 393, 391, 200, 190, 110]
    drill_tool = [52020, 52111, 52112, 52710, 52724, 52801, 52915, 52920, 52925, 52930, 57014, 57015, 57020, 57710, 62011, 62014, 62015, 72011, 72015, 72020, 92310, 92360, 500048]
    spot_drill = [92008, 92020, 92040]
    t_slot_cutter = [910, 915, 905]
    conical_barrel_tool = [8530, 8535, 8540, 8545, 8550]
    chamfered_profile_cutter = [7930, 7940, 7942]
    material_detail = ["FG0001 'HM-MG10'", "FG0002: 'HM'", "FG0003: 'HSS-PM/F'", "FG0004: 'HM-XT'", "FG0005: 'HM-XR'", "FG0006: 'HM-XA'", "FG0007: 'HM-Plus'", "FG0008: 'HM-Micro'", "FG0009 'CBN'", "FG0010: 'HSS-Co8'", "FG0011: 'HM-X10'", "FG0012: 'CVD'", "FG0013: 'HM-MG6'"]

    if tool_id[0].isalpha():
        tool_id = tool_id[1:]
        if tool_id[0] == "0":
            tool_id = tool_id.replace("0", "", 1)
            
    print("TOOL ID: ", tool_id)

    if tool_id.startswith(tuple(str(text_id) for text_id in radius_mill)):
        return "2"
    elif tool_id.startswith(tuple(str(text_id) for text_id in ball_mill)):
        return "3"
    elif tool_id.startswith(tuple(str(text_id) for text_id in end_mill)):
        return "1"
    elif tool_id.startswith(tuple(str(text_id) for text_id in t_slot_cutter)):
        return "6"
    elif tool_id.startswith(tuple(str(text_id) for text_id in conical_barrel_tool)):
        return "conicalBarrelTool"
    elif tool_id.startswith(tuple(str(text_id) for text_id in chamfered_profile_cutter)):
        return "chamferedProfileCutter"
    elif tool_id.startswith(tuple(str(text_id) for text_id in spot_drill)):
        return "spotDrill"
    elif tool_id.startswith(tuple(str(text_id) for text_id in drill_tool)):
        return "4"
    else:
        return "1"


def get_float_property(tool, property_name, default_value="0.0"):
    value = get_property_value(tool, property_name, default_value)
    try:
        return float(value)
    except ValueError:
        return 0.0

def parse_new_xml_data(tool):

    print("Parse the XML file")
    
    #print each element's tag and text
    #for elem in tool.iter():
    #   print(elem.tag, elem.text)
        
    newTool = Tool()

    # Extract the properties using a function to handle missing properties

    newTool.D1 = get_property_value(tool, "A1") or get_property_value(tool, "A11")

    if newTool.D1 == "M":
        print("d1 is M")
        newTool.toolType = "tap"
        newTool.D1 = get_property_value(tool, "A21")  
        newTool.threadPitch = get_property_value(tool, "A3")
        newTool.threadTolerance = get_property_value(tool, "A5")

    newTool.D2 = get_float_property(tool, "A5")
    newTool.D3 = get_float_property(tool, "C3")

    newTool.L1 = get_property_value(tool, "B2") or get_property_value(tool, "B4") or get_property_value(tool, "B3")

    if newTool.toolType == "tap":
        newTool.L2 = get_property_value(tool, "B1")
    else:
        newTool.L2 = get_float_property(tool, "B3")

    newTool.L2 = newTool.L2 or 0 

    newTool.L3 = get_property_value(tool, "B5") or get_property_value(tool, "B3")
    newTool.L3 = float(newTool.L3) if newTool.L3 else 0

    newTool.NoTT = get_property_value(tool, "F21") or get_property_value(tool, "D1")

    newTool.RayonBout = get_float_property(tool, "G1")

    newTool.Chanfrein = get_property_value(tool, "D6")

    print("D1: ", newTool.D1, "D2: ", newTool.D2, "D3: ", newTool.D3, "L1: ", newTool.L1, "L2: ", newTool.L2, "L3: ", newTool.L3, "NoTT: ", newTool.NoTT, "RayonBout: ", newTool.RayonBout, "Chanfrein: ", newTool.Chanfrein)
        


    newTool.ArrCentre = get_property_value(tool, "H21")#int(get_property_value(tool, "H21"))
    #print("Coolants value: ", coolants_value)
    coolants_type = ["0: 'Unkown'","1: 'external'", "2: 'internal'", "3: 'externalAir'", "4: 'externalAir'", "5: 'mql'"]
    #print ("Coolants type: ", coolants_type)
    if newTool.ArrCentre:
        newTool.ArrCentre = int(float(newTool.ArrCentre))
        if newTool.ArrCentre == "0.0"  or not newTool.ArrCentre or newTool.ArrCentre == "No":
            newTool.ArrCentre = 0
        elif newTool.ArrCentre == "1.0":
            newTool.ArrCentre = 1
    else:
        newTool.ArrCentre = 0

    #coolants_value = coolants_type[coolants_value]
    #print("Coolants value: ", coolants_value)

    #coolants_value = coolants_type[coolants_value]


    newTool.GroupeMat = get_property_value(tool, "J3")

   
    newTool.ManufRefSec = get_property_value(tool, "H5")
    newTool.CodeBar = get_property_value(tool, "J21")
    newTool.Comment = get_property_value(tool, "J8")

    newTool.AngleDeg = get_property_value(tool, "E1")

    if newTool.AngleDeg:
        if int(newTool.AngleDeg) > 91 or int(newTool.AngleDeg) < 181:#TODO: check if this is correct
            newTool.toolType = "drill"
        else:
            newTool.toolType = "endMill"

    try:
        newTool.Manuf = tool.find('.//Main-Data/Manufacturer').text.strip()
        newTool.Name = tool.find('.//Main-Data/PrimaryId').text.strip()
    except  Exception as e:
        print("*****name error: ", e)

    if not newTool.Name:
        newTool.Name = tool.find('.//Main-Data/ID21002').text.strip()
    
    print("name: ", newTool.Name)

    manuf_ref = newTool.Name
    #TODO MAKE EXTERNAL EDITABLE LIST
    if newTool.Manuf == "FSA": 
        newTool.Manuf = "FRAISA"
        newTool.toolType = check_fraisa_types(newTool.Name)  # Certifique-se de fornecer o ID correto da ferramenta.

    if newTool.Manuf == "CE":
        newTool.Manuf = "CERATIZIT"    
    if newTool.Manuf == "HOG":
        newTool.Manuf = "HOFFMAN"
    if newTool.Manuf == "JO":
        newTool.Manuf = "JONGEN" 


    
    if not newTool.toolType:
        newTool.toolType = get_property_value(tool, "J22")
        
    if not newTool.toolType:
        newTool.toolType = "1" #TODO: find way to get tool type from xml

    
    #change tslootcutter to tslotMill
    if newTool.toolType == "tslotcutter" or newTool.toolType == "Tslotcutter":
        newTool.toolType = "tslotMill"

    if newTool.toolType == "drilTool":
        newTool.toolType = "drill"

    if newTool.toolType == "NC-Anbohrer":
        newTool.toolType = "spotDrill"

    if newTool.toolType == "Diabolo VHM-Fräser" or newTool.toolType == "Vollhartmetallwerkzeuge. Stahl-. Edelstahl- und Ti":
        newTool.toolType = "endMill"

    print("tool_data: ",newTool.Manuf, newTool.Name, newTool.toolType, newTool.GroupeMat, newTool.AngleDeg, newTool.CoupeCentre, newTool.ArrCentre, newTool.threadTolerance, newTool.threadPitch, newTool.Manuf, newTool.ManufRef, newTool.ManufRefSec, newTool.Code, newTool.CodeBar, newTool.Comment, newTool.CuttingMaterial)

    return newTool

def open_file(self,title,wCard):

    #need to add a file dialog to select multiple the xml files
       
    dlg = wx.FileDialog(self, title, 
                       wildcard=wCard, 
                       style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)
    
    if dlg.ShowModal() == wx.ID_OK:
        xml_file_path = dlg.GetPaths()
        print("PATH", xml_file_path)
        dlg.Destroy()

        if len(xml_file_path) > 1:
            print("More than one file selected")
            #exit()

        if not xml_file_path:
            print('No file seleted.')
            return None
            #exit()



        for path in xml_file_path:
            #print('File selected: ', path)
            
            tree = ET.parse(path)
            #dbout(tree)
            root = tree.getroot()
            #dbout("ROOT",root.tag)
            
            # Try to obtain the 'Tool' element
            #print("Try to get Tool Elem")
            try:
                tool = root.find('.//Tool')
                #dbout("TOOL",tool)
                if tool:
                    tool = parse_new_xml_data(tool)
                else:
                    tool = parse_hyper_xml_data(root)
                
                
                saveTool(tool)

                print("Import xml", path ,"finished")

                print("tool : ", tool)
                if tool:
                    tools = load_tools_from_database(self.panel, self.toolType)
                    print("tools loaded :: ", tools)
                    """self.panel.list_ctrl.Select(self.panel.list_ctrl.GetFirstSelected(),0) #TODO: deselect all 
                    print("Tool added to list:", tool.Name)
                    index = add_line(self.panel, tool)
                    self.panel.list_ctrl.Refresh()
                    """

            except Exception as e:
                print("Error: ", e)
                print("rest :: ", tool)
 

        return tool

   

