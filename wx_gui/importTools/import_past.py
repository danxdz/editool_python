import wx

from tool import Tool
from tool import ToolsCustomData
#from gui.guiTools import getToolTypesNumber
from importTools.validateImportDialogue import validateToolDialog
from importTools import import_past

def open_file(self, title):      
    
    # Read text from clipboard
    text_data = wx.TextDataObject()
    if wx.TheClipboard.Open():
        success = wx.TheClipboard.GetData(text_data)
        wx.TheClipboard.Close()
    if success:
        data = text_data.GetText()
    
        data = str(data)
        len_data = len(data)

        print(len_data , " :: " ,  data)

        if len(data) > 100:
            self.tool = import_past.process_input_13999(data, self.toolData.tool_types_list)
            #print("tool :: ", self.tool)
        else:
            #lets process data without headers
            #divide data by tab and spaces into list
            tool_data = data.split()
            for element in tool_data:
                print(element)

            #strip M from tool diameter
            self.tool.name = tool_data[0]
            self.tool.D1 = tool_data[1]
            if self.tool.D1[0] == 'M':
                #check if it is a threadMill , if its number is a threadMill, if is '6HX' one number and letters its a tap
                for letter in tool_data[3]:
                    if letter.isalpha():
                        self.tool.toolType = 8
                        break
                if self.tool.toolType == 9:
                    # 167081	M1.4	1.06	0.300	39.0	0.6	6	3.00	3	1.10
                    print("threadMill")
                    #self.tool.toolType = 9
                    self.tool.D1 = self.tool.D1[2:]
                    self.tool.D2 = tool_data[2]
                    self.tool.threadPitch = tool_data[3]
                    self.tool.L3 = tool_data[4]
                    self.tool.L1 = tool_data[5]
                    self.tool.L2 = tool_data[6]
                    self.tool.D3 = tool_data[7]
                    self.tool.z = tool_data[8]
                else:
                    # 176692	M8	8.00	6H 	1.250 	90.0 	20.0 	6.00 	4.9 	2 	6.80
                    print("tap")
                    self.tool.toolType = 5
                    self.tool.D1 = tool_data[2]
                    self.tool.threadTolerance = tool_data[3]
                    self.tool.threadPitch = tool_data[4]
                    self.tool.L3 = tool_data[5]
                    self.tool.L1 = tool_data[6]
                    self.tool.D3 = tool_data[7]
                    self.tool.z = tool_data[9] 


        validateToolDialog(self.panel, self.tool, True).ShowModal()


def process_input_13999(input_text, toolTypesList):

    toolData = ToolsCustomData()


    # Parse the config file to create the mapping
    with open("13999_paste.txt",  encoding='UTF-8') as config_file:
        config_text = config_file.read()
    config_lines = config_text.split('\n')
    name_mapping = {}
    for line in config_lines:
        parts = line.split(';')
        #print("parts: ", parts)
        if len(parts) >= 4 and parts[0].isdigit():
            name_mapping[parts[1]] = parts[2].replace('@', '')
            #print("parts filter: ", parts)


    print("name_mapping: ", name_mapping)
    # Parse the input text and populate the Tool object
    lines = input_text.split('\n')
    #for line in lines: 
        #print("line: ", line)
        
    tool = Tool()
    for line in lines:
        parts = line.split('\t')
        print("parts: ", parts, len(parts))
        if len(parts) == 3:
            # Use the mapping to get the attribute name
            attr_name = name_mapping.get(parts[0])#.replace(' ', ''))
            if attr_name is not None:
                print("attr_name: ", attr_name, parts[2].replace(' mm', ''))
                setattr(tool, attr_name, parts[2].replace(' mm', ''))

    if tool.toolType == "":
        detectedToolType = detect_tool_type(float(tool.D1), float(tool.cornerRadius))
        print("detectedToolType: ", detectedToolType)
        tool.toolType = detectedToolType


    if tool.name == "":
        # Extract the manufacturer code (ManufRef) from the first line (Name = ManufRef)
        first_line = lines[0].strip().split(' ')
        print("first_line: ", first_line)
        tool.mfrRef = first_line[0]
        print("tool.ManufRef: ", tool.mfrRef)
        tool.name = tool.mfrRef
        print("tool.Name: ", tool.name)
    if tool.mfr == "":
        tool.mfr, tool.mfrSecRef = detect_tool_manuf(tool.name)

    if tool.coolantType == "Yes":
        tool.coolantType = "1"
    else:
        tool.coolantType = "0"


    return tool


def detect_tool_type(diameter, cornerRadius):
    # verify if it is a ballMill based on the tip radius
    print("detect_tool_type: D: " + str(diameter) + " r: " + str(cornerRadius))
    if cornerRadius == diameter / 2:
        return 2#"ballMill"
    
    # verify if it is a radiusMill based on the tip radius
    if cornerRadius > 0.15:  # 0.1 is the minimum tip radius to be considered a radiusMill
        return 1#"radiusMill"
    
    #else assume it is a endMill
    return 0



def detect_tool_manuf(name):
    print("detect_tool_manuf: " + name)
    patterns = {
        'J': 'Jabro - VHM General machining',
        'JC': 'Jabro - Composites Composite machining',
        'JD': 'Jabro - Diamond Graphite machining',
        'JH': 'Jabro - HSM/Tornado High speed machining',
        'JHF': 'Jabro - HFM High feed machining',
        'JHP': 'Jabro - HPM High performance machining',
        'JM': 'Jabro - Mini Micro machining',
        'JS': 'Jabro - Solid General machining',
        'JPD': 'Jabro - Composites Composite machining',
        'JCO': 'Jabro - HSS-E General machining',
        'JCG': 'Jabro - Ceramic High performance machining',
        'XS': 'X-Heads - Solid2 High performance machining',
        'XH': 'X-Heads - HSM/Tornado High speed machining',
        'XV': 'X-Heads - VHM General machining',
        'XHF': 'X-Heads - HFM High feed machining',
        '440': 'High speed',
        'SMB': 'JABRO MINI' 
    }

    for code, pattern in patterns.items():
        if name.startswith(code):
            return  'SECO', pattern

    return None, None
