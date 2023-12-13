from tool import Tool

def process_input_13999(input_text):
    # Parse the config file to create the mapping
    with open("13999_paste.txt") as config_file:
        config_text = config_file.read()
    config_lines = config_text.split('\n')
    name_mapping = {}
    for line in config_lines:
        parts = line.split(';')
        print("parts: ", parts)
        if len(parts) >= 4 and parts[0].isdigit():
            name_mapping[parts[1]] = parts[2].replace('@', '')
            print("parts filter: ", parts)


    print("name_mapping: ", name_mapping)
    # Parse the input text and populate the Tool object
    lines = input_text.split('\n')
    for line in lines: 
        print("line: ", line)
        
    tool = Tool()
    for line in lines:
        parts = line.split('\t')
        if len(parts) == 3:
            # Use the mapping to get the attribute name
            attr_name = name_mapping.get(parts[0].replace(' ', ''))
            if attr_name is not None:
                setattr(tool, attr_name, parts[2].replace(' mm', ''))

    if tool.toolType == "":
        tool.toolType = detect_tool_type(float(tool.D1), float(tool.RayonBout))

    if tool.Name == "":
        # Extract the manufacturer code (ManufRef) from the first line (Name = ManufRef)
        first_line = lines[0].strip().split(' ')
        print("first_line: ", first_line)
        tool.ManufRef = first_line[0]
        print("tool.ManufRef: ", tool.ManufRef)
        tool.Name = tool.ManufRef
        print("tool.Name: ", tool.Name)
    if tool.Manuf == "":
        tool.Manuf, tool.ManufRefSec = detect_tool_manuf(tool.Name)


    return tool


def detect_tool_type(diameter, tip_radius):
    # Verifica se a ferramenta tem um raio de ponta significativo para ser considerada ballMill (fresa esférica)
    print("detect_tool_type: D: " + str(diameter) + " r: " + str(tip_radius))
    if tip_radius == diameter / 2:
        return "ballMill"
    
    # Verifica se a ferramenta tem raio de ponta igual a zero ou insignificante para ser considerada endMill (fresa de topo)
    if tip_radius > 0.1:  # Ajuste o valor conforme necessário para definir o limite do raio insignificante
        return "radiusMill"
    
    # Se não se encaixar em nenhuma das categorias anteriores, assume-se que é uma radiusMill (fresa com raio de ponta)
    return "endMill"



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
    }

    for code, pattern in patterns.items():
        if name.startswith(code):
            return  'SECO', pattern

    return None, None


"""

    tool_data = {
        'Name': tool.Name,
        'toolType': tool.toolType,
        'GroupeMat': tool.GroupeMat,
        'D1': float(tool.D1),
        'D2': float(tool.D2),
        'D3': float(tool.D3),
        'L1': float(tool.L1),
        'L2': float(tool.L2),
        'L3': float(tool.L3),
        'NoTT': int(tool.NoTT),
        'RayonBout': float(tool.RayonBout),
        'Chanfrein': float(tool.Chanfrein),
        'CoupeCentre': float(tool.CoupeCentre),
        'ArrCentre': tool.ArrCentre,
        'TypeTar': int(tool.TypeTar),
        'PasTar': float(tool.PasTar),
        'Manuf': tool.Manuf,
        'ManufRef': tool.ManufRef,
        'ManufRefSec': tool.ManufRefSec,
        'Code': tool.Code,
        'CodeBar': tool.CodeBar,
        'Comment': tool.Comment,
    }
    print("tool_data: ", tool_data)
    return Tool(**tool_data)
"""