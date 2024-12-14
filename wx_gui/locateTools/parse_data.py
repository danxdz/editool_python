import json

#import Tool
from tool import Tool

def parse_dimension(value_str):
    """Parse a dimension string like '12.00 mm' and return the numerical value."""
    if value_str:
        parts = value_str.strip().split()
        value = parts[0].replace(',', '.')
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0

def get_value(data, key):
    val = data.get(key, '')
    if isinstance(val, dict):
        return val.get('value', '')
    else:
        return val

def parse_tool_data(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check if the data contains valid tool attributes APMXS and LU and APMX
    l1 = next((parse_dimension(get_value(data, key)) for key in ['APMXS', 'LU', 'APMX'] if parse_dimension(get_value(data, key))), 0.0)
    l2 = next((parse_dimension(get_value(data, key)) for key in ['LB_1', 'LN', 'LH', 'LPR'] if parse_dimension(get_value(data, key))), l1)

    #check if tooltype is an integer
    if not isinstance(data.get('toolType', ''), int):
        #try to convert it to an integer
        try:
            data['toolType'] = int(data.get('toolType', ''))
        except ValueError:
            data['toolType'] = 0

    # Initialize the tool attributes with default values
    tool_attrs = {
        'name': data.get('name', ''),
        'toolType': data.get('toolType', 0),
        'cuttingMaterial': get_value(data, 'TMC1ISO'),
        'toolMaterial': get_value(data, 'GRADE'),
        'D1': parse_dimension(get_value(data, 'DC')) if get_value(data, 'DC') else parse_dimension(get_value(data, 'D1')) ,
        'D2': parse_dimension(get_value(data, 'DN')),
        'D3': parse_dimension(get_value(data, 'DMM')) if get_value(data, 'DMM') else parse_dimension(get_value(data, 'DCONMS')),
        'L1': l1 ,
        'L2': l2 ,
        'L3': parse_dimension(get_value(data, 'OAL')) if get_value(data, 'OAL') else parse_dimension(get_value(data, 'LF')),
        'z': int(parse_dimension(get_value(data, 'PCEDC'))) if get_value(data, 'PCEDC') else int(parse_dimension(get_value(data, 'ZEFP'))),
        'cornerRadius': parse_dimension(get_value(data, 'RE')),
        'chamfer': parse_dimension(get_value(data, 'CHW')) if get_value(data, 'CHW') else parse_dimension(get_value(data, 'KAPR')) ,
        'neckAngle': parse_dimension(get_value(data, 'FHA')) if get_value(data, 'FHA') else parse_dimension(get_value(data, 'SIG')),
        'centerCut': int(parse_dimension(get_value(data, 'CCC'))),
        'coolantType': int(parse_dimension(get_value(data, 'CSP'))),
        'threadTolerance': get_value(data, 'TCDCON'),
        'threadPitch': 0.0,  # Map from data if available
        'code': get_value(data, 'Numéroarticle'),
        'codeBar': get_value(data, 'Code barre'),
        'mfr': get_value(data, 'mfr'),
        'mfrRef': get_value(data, 'mfrRef'),
        'mfrSecRef': get_value(data, 'mfrSecRef'),
        'comment': data.get('comment', ''),
        'TSid': '',  # Map from data if available
    }

    # Create an instance of the Tool class with the parsed attributes
    tool = Tool(**tool_attrs)
    return tool
