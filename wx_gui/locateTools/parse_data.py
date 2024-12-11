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

    # Initialize the tool attributes with default values
    tool_attrs = {
        'name': data.get('name', ''),
        'toolType': 0,  # TODO: Determine based on data
        'cuttingMaterial': get_value(data, 'TMC1ISO'),
        'toolMaterial': get_value(data, 'GRADE'),
        'D1': parse_dimension(get_value(data, 'DC')),
        'D2': parse_dimension(get_value(data, 'DN')),
        'D3': parse_dimension(get_value(data, 'DMM')) if get_value(data, 'DMM') else parse_dimension(get_value(data, 'DCONMS')),
        'L1': parse_dimension(get_value(data, 'APMXS')) if get_value(data, 'APMXS') else parse_dimension(get_value(data, 'LU')) ,
        'L2': parse_dimension(get_value(data, 'LN')) if get_value(data, 'LN') else parse_dimension(get_value(data, 'LB_1')) ,
        'L3': parse_dimension(get_value(data, 'OAL')) if get_value(data, 'OAL') else parse_dimension(get_value(data, 'LF')),
        'z': int(parse_dimension(get_value(data, 'PCEDC'))) if get_value(data, 'PCEDC') else int(parse_dimension(get_value(data, 'ZEFP'))),
        'cornerRadius': parse_dimension(get_value(data, 'RE')),
        'chamfer': parse_dimension(get_value(data, 'CHW')) if get_value(data, 'CHW') else parse_dimension(get_value(data, 'KAPR')) ,
        'neckAngle': parse_dimension(get_value(data, 'FHA')),
        'centerCut': int(parse_dimension(get_value(data, 'CCC'))),
        'coolantType': int(parse_dimension(get_value(data, 'CSP'))),
        'threadTolerance': get_value(data, 'TCDCON'),
        'threadPitch': 0.0,  # Map from data if available
        'code': get_value(data, 'Numéroarticle'),
        'codeBar': get_value(data, 'Code barre'),
        'mfr': get_value(data, 'mfr'),
        'mfrRef': data.get('name', ''),
        'mfrSecRef': '',  # Map from data if available
        'comment': '',  # Add any additional comments if needed
        'TSid': '',  # Map from data if available
    }

    # Create an instance of the Tool class with the parsed attributes
    tool = Tool(**tool_attrs)
    return tool
