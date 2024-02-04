import wx
import xml.etree.ElementTree as ET

import csv

#from gui.guiTools import getToolTypesNumber

from tool import Tool, ToolsDefaultsData

tools_defaults = ToolsDefaultsData()

def parse_hyper_xml_data(root):
    print(":: import from XML hp fraisa type")
    
    # Obtém os dados da ferramenta
    tool = root.find('.//tool')
    #dbout("TOOL",tool)
    # Find the tecset with type="milling"
    milling_tecset = tool.find(".//tecset")

    # Extract the value of the 'coolants' parameter from the milling_tecset
    coolants_value = milling_tecset.find(".//param[@name='coolants']").attrib['value']
    #print("Coolants value: ", coolants_value)

    #print(tool.attrib['name'])
    
    coolantType = coolants_value
    #print("coolant: ", coolantType)
    
    toolType = tool.attrib['type']

    #check if toolType is not empty
    #print("Tool type hyper: ")
    #print(toolType)


    #check if toolType is valid
    if not toolType:
        toolType == 0
    else:
        print("teset: ", toolType)
        #tooltype where is a string, like "endmill", need to enumerate from tools_defaults.tool_types
        if toolType in tools_defaults.tool_types:
            toolType = tools_defaults.tool_types.index(toolType)
           
        
    name = tool.attrib['name']
    #print("name: ", name)
    cutMat = tool.find('param[@name="cuttingMaterial"]').attrib['value']
    #print("GroupMat: ", groupMat)
    d1 = float(tool.find('param[@name="toolDiameter"]').attrib['value'])
    #print("D1: ", d1)
    d2 = float(tool.find('param[@name="toolDiameter"]').attrib['value'])-0.2
    #print("D2: ", d2)
    d3 = tool.find('param[@name="toolShaftDiameter"]').attrib['value']
    if d3:
        d3 = float(d3)
        #print("D3: ", d3)

    l1 = float(tool.find('param[@name="cuttingLength"]').attrib['value'])
    #print("L1: ", l1)
    l2 = float(tool.find('param[@name="taperHeight"]').attrib['value'])
    #print("L2: ", l2)
    l3 = float(tool.find('param[@name="toolTotalLength"]').attrib['value'])
    #print("L3: ", l3)

    z = tool.find('param[@name="cuttingEdges"]').attrib['value']
    if z:
        z = int(z)
        #print("z: ", z)

        
    cornerRadius = tool.find('param[@name="cornerRadius"]').attrib['value']
    if cornerRadius:
        cornerRadius = float(cornerRadius)
        #print("cornerRadius: ", cornerRadius)
        
    
    chamfer = tool.find('param[@name="toolShaftChamferAbsPos"]').attrib['value']
    if chamfer:
        chamfer = chamfer
        #print("chamfer: ", chamfer)


    mfr = tool.find('param[@name="manufacturer"]').attrib['value']
    print("mfr: ", mfr)

    codeBar = tool.find('param[@name="orderingCode"]').attrib['value']
    #print("CodeBar: ", codeBar)
    
    comment = tool.find('param[@name="comment"]').attrib['value']
    #print("Comment: ", comment)

        
    tool_data = {
        # Adicione essa linha para obter o atributo 'name' do XML
        'name': name,
        'toolType': toolType,
        'D1': d1,
        'D2': d2,
        'D3': d3,
        'L1': l1,
        'L2': l2,
        'L3': l3,
        'z': z,
        'cornerRadius': cornerRadius,
        'chamfer': chamfer,
        'centerCut': "no",
        'coolantType': coolantType,
        'threadPitch': 0,
        'threadTolerance': "",
        'cuttingMaterial': cutMat,
        'mfr': mfr,
        'mfrRef': tool.find('param[@name="orderingCode"]').attrib['value'],
        'mfrSecRef': "",
        'code': " ",
        'codeBar': codeBar,
        'comment': comment,
    }



    newTool = Tool(**tool_data) 
    for key, value in newTool.getAttributes().items():
        print(key, value)

    newTool.toolType = fix_toolType(newTool)

    return newTool



def get_category_value(tool, catProp,  prop_name, default_value=''):
    properties = tool.findall(catProp)#".//Category-Data"
    for prop in properties:
        prop_name_elem = prop.find("PropertyName[@source='din_mk']")
        if prop_name_elem is not None and prop_name_elem.text == prop_name:
            value_elem = prop.find("Value")
            value = value_elem.text.strip()
            value = value.replace(',', '.')
            if value_elem is not None and value:
                try:
                    return value
                except ValueError:
                    return value
    return default_value


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
    frTooltypes = []

    radiusMill = [840, 8107, 8720, 15502, 15572, 15573, 15574, 15575, 15582, 15583, 15584, 15585, 8507, 6032, 6034, 6036, 6038, 6040, 6042, 6044, 7284, 7288, 7340, 7344, 7620, 7624, 15268, 5257, 45319, 500022, 500023, 500024, 500025, 500046, 500047, 500048, 500049, 500050, 500051, 500052, 500053, 500054, 500055, 500056, 500057, 500058, 500059, 500060, 500061, 500062, 500063, 500064, 500065, 500066, 500067, 500068, 500069, 500070, 500071, 500072, 500073, 500074, 500075, 500076, 500077, 500085, 500086, 8617, 8117, 5234, 5250, 5252, 5640, 5645, 5650, 5752, 5754, 5756, 5762, 5764, 6531, 6532, 6533, 6534, 6535, 6536, 6538, 6735, 6736, 6738, 6740, 6742, 6744, 7100, 7104, 7200, 7204, 7600, 7604, 7608, 15226, 31410, 31420, 35400, 95752, 95754, 95756, 7210, 15512, 7610, 7612, 7614, 7212, 6816, 6818, 6820, 6823]
    ballMill = [6062, 6064, 6066, 6068, 6070, 6072, 6074, 7400, 7404, 7408, 7460, 7464, 7484, 7488, 7500, 7540, 7544, 7550, 7402, 7554, 5286, 5288, 5289, 5580, 5782, 5784, 5786, 5787, 5791, 5792, 5793, 5794, 5796, 6460, 6461, 6462, 6463, 6464, 6481, 6482, 6483, 6560, 6561, 6562, 6563, 6564, 6565, 6566, 6567, 6568, 6579, 6581, 6582, 6583, 6765, 6766, 6768, 6770, 6772, 6774, 7450, 7454, 7458, 7470, 7474, 7478, 15781, 15795, 31700, 35700, 45298, 45785, 95782, 95784, 95786, 95787, 95791, 95793, 915795, 7472, 7490, 7492, 7494, 6832, 6836, 6840, 6844, 6846, 6847, 6848, 6849]
    endMill = [500043, 500042, 500041, 500040, 500015, 500014, 500013, 500012, 500011, 500010, 500009, 500008, 500007, 500006, 500005, 500004, 500003, 500002, 500001, 500000, 95717, 95716, 95714, 95712, 46310, 46300, 45713, 45710, 45709, 45372, 45371, 45362, 45360, 45355, 45336, 45334, 45333, 45326, 45325, 45323, 45322, 45317, 20030, 20025, 20020, 15754, 15752, 15725, 15711, 15607, 15606, 15590, 15589, 15561, 15560, 15559, 15557, 15550, 15535, 15530, 15525, 15520, 15510, 15507, 15506, 15505, 15500, 15359, 15299, 15298, 15297, 15260, 15254, 15251, 15250, 15248, 15242, 15239, 15238, 15236, 15233, 15232, 15225, 15223, 15222, 15210, 15208, 15207, 8805, 8800, 8618, 8616, 8614, 8608, 8606, 8604, 8521, 8502, 8500, 8404, 8323, 8321, 8320, 8315, 8313, 8311, 8310, 8305, 8303, 8302, 8301, 8300, 8121, 8115, 8112, 8111, 8105, 8102, 8101, 8100, 6812, 6811, 6810, 6809, 6807, 6804, 6802, 6800, 6508, 6506, 6505, 6504, 6503, 6502, 6501, 6500, 5724, 5723, 5722, 5721, 5717, 5716, 5714, 5712, 5400, 5336, 5335, 5329, 5297, 5279, 5272, 5255, 5249, 5237, 5225, 5219, 5218, 5215, 5214, 5213, 5200, 5036, 780, 700, 695, 665, 659, 650, 621, 619, 610, 609, 540, 410, 400, 393, 391, 200, 190, 110]
    spotDrill = [92008, 92020, 92040]
    drill = [52020, 52111, 52112, 52710, 52724, 52801, 52915, 52920, 52925, 52930, 57014, 57015, 57020, 57710, 62011, 62014, 62015, 72011, 72015, 72020, 92310, 92360, 500048]
    tslotMill = [910, 915, 905]
    conical_barrel_tool = [8530, 8535, 8540, 8545, 8550]
    chamferMill = [7930, 7940, 7942]

    frTooltypes.append(endMill)
    frTooltypes.append(radiusMill)
    frTooltypes.append(ballMill)
    frTooltypes.append(chamferMill)
    frTooltypes.append(tslotMill)
    frTooltypes.append(spotDrill)
    frTooltypes.append(spotDrill)#centerDrill
    frTooltypes.append(drill)
    frTooltypes.append(conical_barrel_tool)
    
    material_detail = ["FG0001 'HM-MG10'", "FG0002: 'HM'", "FG0003: 'HSS-PM/F'", "FG0004: 'HM-XT'", "FG0005: 'HM-XR'", "FG0006: 'HM-XA'", "FG0007: 'HM-Plus'", "FG0008: 'HM-Micro'", "FG0009 'CBN'", "FG0010: 'HSS-Co8'", "FG0011: 'HM-X10'", "FG0012: 'CVD'", "FG0013: 'HM-MG6'"]

    if tool_id[0].isalpha():
        tool_id = tool_id[1:]
        if tool_id[0] == "0":
            tool_id = tool_id.replace("0", "", 1)
              
    #check all tool types
    for i, toolType in enumerate(frTooltypes):
        if tool_id.startswith(tuple(str(text_id) for text_id in toolType)):
            #print("toolType fsa: ", i)
            return i
    return -1


def get_float_property(tool, property_name, default_value="0.0"):
    value = get_property_value(tool, property_name, default_value)
    try:
        return float(value)
    except ValueError:
        return 0.0

def parse_new_xml_data(tool):

    print(":: import from XML")
    
    #print each element's tag and text
    #for elem in tool.iter():
    #   print(elem.tag, elem.text)
        
    newTool = Tool()

    readDin = get_category_value(tool,".//Category-Data",  "NSM", )
    #print("readDin: ", readDin)
    readType = get_category_value(tool,".//Category-Data", "BLD")
    #print("readType: ", readType)

    if readDin == "DIN4000-80": 
        '''DIN4000-80 - Screwing taps, cold forming taps and screwing dies'''
        #switch readType
        match readType:
            case "1":
                #print(f"{readType} - toolType is EndMill")
                '''DIN4000-80-1 - Taps with slim shank'''
                newTool.toolType = 0
            case "2":
                #print(f"{readType} - toolType is Tap")
                """DIN4000-80-2 - Taps with reinforced shank"""
                newTool.toolType = 8
            case "3":
                #print(f"{readType} - toolType is Tap")
                """DIN4000-80-3 - Forming taps with slim shank"""
                newTool.toolType = 8
            case "4":
                """DIN4000-80-4 - Forming taps with reinforced shank"""
                #print(f"{readType} - toolType is Tap")
                newTool.toolType = 8


    if readDin == "DIN4000-81": #DIN4000-81 - Drills and countersinking tools with non-indexable cutting edges
        #switch readType
        match readType:
            case "1":
                #print(f"{readType} - toolType is Drill")
                newTool.toolType = 7                
                newTool.D1 = get_property_value(tool, "A11")
            case "6":
                #print(f"{readType} - toolType is spotDrill")
                newTool.toolType = 5
            case "7":
                #print(f"{readType} - toolType is centerDrill")
                newTool.toolType = 6
                newTool.D1 = get_property_value(tool, "A11")
                newTool.D2 = get_property_value(tool, "A11_2")
                newTool.D3 = get_property_value(tool, "C3")
                newTool.L1 = get_property_value(tool, "B4") or get_property_value(tool, "B2_2")
                newTool.L2 = get_property_value(tool, "B3")
                newTool.L3 = get_property_value(tool, "B5")
                newTool.chamfer = get_property_value(tool, "E4_2")


    if readDin == "DIN4000-82": #DIN4000-82 - End mills with non-indexable cutting edges
        #switch readType
        match readType:
            case "1":
                #print(f"{readType} - toolType is EndMill")
                '''DIN4000-82-1 - End milling cutters'''
                newTool.toolType = 0
            case "2":
                #print(f"{readType} - toolType is RadiusMill")
                '''DIN4000-82-2 - Slotting and milling cutters'''
                if newTool.cornerRadius:
                    if newTool.cornerRadius > 0.2:
                        newTool.toolType = 1
                    else:
                        newTool.toolType = 0
            case "3":
                #print(f"{readType} - toolType is ChamferMill")
                '''DIN4000-82-3 - Angle milling cutters'''
                newTool.toolType = 3
            case "4":
                print(f"{readType} - toolType is InversedChamferMill- not supported")
                '''DIN4000-82-4 - Angle milling cutters (rev)'''
                newTool.toolType = -1
            case "5":
                #print(f"{readType} - toolType is TSlotMill")
                '''DIN4000-82-5 - Fraise à rainure en T'''
                newTool.toolType = 4
            case "6":
                #print(f"{readType} - toolType is BallMill")
                '''DIN4000-82-6 - Ball nose milling cutters'''
                newTool.toolType = 2
            case "7":
                #print(f"{readType} - toolType is BallMill - copy tool")
                '''DIN4000-82-7 - Die end milling cutters'''
                newTool.toolType = 2
            case "8":
                print(f"{readType} - toolType is Rounded profile end mill - not supported")
                '''DIN4000-82-8 - Rounded profile end mill, concave'''
                newTool.toolType = -1
            case "9":
                #print(f"{readType} - toolType is milling burrs - not supported")
                '''DIN4000-82-9 - Milling burrs'''
                newTool.toolType = 7
            case "10":
                #print(f"{readType} - toolType is ThreadMill")
                '''DIN4000-82-10 - Thread milling cutters'''
                newTool.toolType = 9
            case "11":
                print(f"{readType} - toolType is Gouges - not supported")
                '''DIN4000-82-11 - Gouges'''
                newTool.toolType = -1
            case "12":
                #print(f"{readType} - toolType is ThreadMill")
                '''DIN4000-82-12 - Drill thread milling cutters'''
                newTool.toolType = 9

        print(f"toolType detected: {readDin}-{readType} :: {tools_defaults.tool_types[newTool.toolType]}")



    # Extract the properties using a function to handle missing properties
    if readDin == "DIN4000-82" or readDin == "DIN4000-80":
        newTool.D1 = get_property_value(tool, "A1") or get_property_value(tool, "A11")
        if newTool.D1 == "M":
            #print("d1 is M")
            newTool.D1 = get_property_value(tool, "A21")  
            newTool.D3 = get_property_value(tool, "C3")
            newTool.L1 = get_property_value(tool, "B1")
            newTool.L2 = get_property_value(tool, "B2")
            newTool.threadPitch = get_property_value(tool, "A3")
            newTool.threadTolerance = get_property_value(tool, "A5")
            


    if not newTool.D1 and not newTool.toolType:
        print("no d1")
        newTool.D1 = get_property_value(tool, "A2")  or  get_property_value(tool, "A11")      
        
    if not newTool.D2:
        newTool.D2 = get_float_property(tool, "A5")
    
    if not newTool.L1:
        newTool.L1 = get_property_value(tool, "B2") or get_property_value(tool, "B4") or get_property_value(tool, "B3") #b2 fraisa
    if not newTool.L2:
        newTool.L2 = get_property_value(tool, "B9") #fraisa


    if not newTool.D3:
        newTool.D3 = get_float_property(tool, "C3")
    
    newTool.L3 = get_property_value(tool, "B5") or get_property_value(tool, "B3")
    newTool.z = get_property_value(tool, "F21") or get_property_value(tool, "D1")
    newTool.cornerRadius = get_float_property(tool, "G1")

    #print("D1: ", newTool.D1, "D2: ", newTool.D2, "D3: ", newTool.D3, "L1: ", newTool.L1, "L2: ", newTool.L2, "L3: ", newTool.L3, "z: ", newTool.z, "cornerRadius: ", newTool.cornerRadius, "chamfer: ", newTool.chamfer)
        
    newTool.coolantType = get_property_value(tool, "H21")
    
    if newTool.coolantType:
        newTool.coolantType = int(float(newTool.coolantType))
        if newTool.coolantType == "0.0"  or not newTool.coolantType or newTool.coolantType == "No":
            newTool.coolantType = 0
        elif newTool.coolantType == "1.0":
            newTool.coolantType = 1
    else:
        newTool.coolantType = 0


    newTool.toolMaterial = get_property_value(tool, "J3")   
    newTool.mfrSecRef = get_property_value(tool, "H5")
    newTool.codeBar = get_property_value(tool, "J21")
    newTool.comment = get_property_value(tool, "J8")
    newTool.neckAngle = get_property_value(tool, "E1")
    if not newTool.toolType:
        newTool.toolType = get_property_value(tool, "D11")

    if newTool.toolType == 9:#threadMill
        #print("toolType is ThreadMill")
        newTool.D1 = get_float_property(tool, "A5") or get_float_property(tool, "A2")
        newTool.D2 = 0 #no D2 for threadMill
        newTool.threadPitch = get_property_value(tool, "D32") 
        newTool.threadTolerance = get_property_value(tool, "D31")  

        findB4 = get_property_value(tool, "B4")
        #print("findB4: ", findB4)
        if findB4:
            newTool.L1 = get_float_property(tool, "B2")
            newTool.L2 = findB4
        else:
            newTool.L2 = get_property_value(tool, "B2")

    if newTool.neckAngle:
        if not newTool.toolType:
            #print("no toolType")
            if int(newTool.neckAngle) > 91 or int(newTool.neckAngle) < 181 and not newTool.toolType:
                newTool.toolType = 7#drill
        

    try:
        newTool.mfr = tool.find('.//Main-Data/Manufacturer').text.strip()
        #print("mfr: ", newTool.mfr)
        newTool.name = tool.find('.//Main-Data/PrimaryId').text.strip()
    except  Exception as e:
        print("*****name error: ", e)


    if not newTool.name:
        newTool.name = tool.find('.//Main-Data/ID21002').text.strip()
    
    #print("name: ", newTool.name)
    
    if not newTool.mfr:
        newTool.mfr = get_property_value(tool, "J3")

    #TODO MAKE EXTERNAL EDITABLE LIST
    if newTool.mfr == "FSA": 
        newTool.mfr = "FRAISA"
        newTool.toolType = check_fraisa_types(newTool.name)  
        #print("found FRAISA tool_type :: ", newTool.toolType)

    if newTool.mfr == "CE":
        newTool.mfr = "CERATIZIT"    
    if newTool.mfr == "HOG":
        newTool.mfr = "HOFFMAN"
    if newTool.mfr == "JO":
        newTool.mfr = "JONGEN" 
    
    if newTool.toolType == "":
       newTool.toolType = get_property_value(tool, "J22")
       #print("new toolType: J22  ", newTool.toolType)
    
    if not newTool.toolType:
        newTool.toolType = 0 #TODO: find way to get tool type from xml 
        newTool.tooltype = fix_toolType(newTool)

    #print("tool_data: ",newTool.mfr, newTool.name, newTool.toolType, newTool.cuttingMaterial, newTool.neckAngle, newTool.centerCut, newTool.coolantType, newTool.threadTolerance, newTool.threadPitch, newTool.mfr, newTool.mfrRef, newTool.mfrSecRef, newTool.code, newTool.codeBar, newTool.comment)

    #alert if toolType is not valid
    if not newTool.D1 or newTool.D1 == 0 or newTool.D1 == "0":
        #print("no D1", newTool.D1)
        msgError = wx.MessageBox("Tool cut diameter not detected", "Warning", wx.OK | wx.ICON_WARNING)

    return newTool

def fix_toolType(newTool):
    
    if newTool.toolType == "Diabolo VHM-Fräser" or newTool.toolType == "Vollhartmetallwerkzeuge. Stahl-. Edelstahl- und Ti":
        newTool.toolType = 0

    if newTool.toolType == "Eckradiusfräser" or newTool.toolType == "VHM-Torusfräser":
        newTool.toolType = 1
        
    #change tslootcutter to tslotMill
    if newTool.toolType == "tslotcutter" or newTool.toolType == "Tslotcutter":
        newTool.toolType = 4


    if newTool.toolType == "NC-Anbohrer":
        newTool.toolType = 5

    if newTool.toolType == "drillTool":
        newTool.toolType = 7

    if newTool.toolType == "Trennstellenkodierung maschinenseitig":
        newTool.toolType = 9
    
    return newTool.toolType
    

def open_file(self,title,wCard):

       
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


        toolsList = []

        toolData = ToolsDefaultsData()       


        for path in xml_file_path:
            #print('File selected: ', path)
            
            tree = ET.parse(path)
            #dbout(tree)
            root = tree.getroot()
            #dbout("ROOT",root.tag)
            
            # Try to obtain the 'Tool' element to check XML type
            try:
                tool = root.find('.//Tool')
                #dbout("TOOL",tool)
                if tool:
                    tool = parse_new_xml_data(tool)
                else:
                    tool = parse_hyper_xml_data(root)

                print("Import xml", path ,"finished")
                print("tool: ", tool.name, tool.toolType, tool.toolMaterial, tool.D1, tool.D2, tool.D3, tool.L1, tool.L2, tool.L3, tool.z, tool.cornerRadius, tool.chamfer, tool.centerCut, tool.coolantType, tool.threadPitch, tool.mfr, tool.mfrRef, tool.mfrSecRef, tool.code, tool.codeBar, tool.comment)
                toolsList.append(tool)



                '''                # Caminho do arquivo CSV
                                csv_file_path = "ferramentas.csv"


                                add_tools_to_csv(toolsList, csv_file_path)

                                # Lê as ferramentas do arquivo CSV
                                loaded_tools = read_tools_from_csv(csv_file_path)

                                # Exibir ferramentas carregadas
                                for tool in loaded_tools:
                                    print(tool)
'''
                                        
                        
                        
            except Exception as e:
                print("Error: ", e)
                print("rest :: ", tool)

        print("toolsList :: ", len(toolsList))
        return toolsList



# Adiciona ferramentas ao arquivo CSV sem cabeçalho
def add_tools_to_csv(tools, file_path):
    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Adiciona as ferramentas sem verificar o cabeçalho
        for tool in tools:
            writer.writerow(tool.getAttributes().values())

# Lê as ferramentas do arquivo CSV
def read_tools_from_csv(file_path):
    loaded_tools = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            loaded_tools.append(row)
    return loaded_tools

