from tool import Tool
from tool import ToolsCustomData
#from gui.guiTools import getToolTypesNumber
from importTools.validateImportDialogue import validateToolDialog

def open_file(self, title):      
    tool = Tool()  
    validateToolDialog(self.panel, tool).ShowModal()


def process_input_13999(input_text, toolTypesList):

    toolData = ToolsCustomData()


    # Parse the config file to create the mapping
    with open("13999_paste.txt") as config_file:
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
