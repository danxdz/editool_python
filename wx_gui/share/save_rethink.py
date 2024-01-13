from rethinkdb import r

from tool import ToolsDefaultsData

def testdb (tool):

    tools_def_data = ToolsDefaultsData()

    tools_types_list = tools_def_data.tool_types  
    new_table = tools_types_list[tool.toolType]

    r.connect('localhost', 28015).repl()
    try:
        r.db('test').table_create(new_table).run()
    except:
        print("table already exists: " + new_table)
        
    r.table(new_table).insert([
    { "name": tool.name , "toolMat": tool.toolMaterial, "cutMat": tool.cuttingMaterial, 
     "d1": tool.D1, "d2": tool.D2, "d3": tool.D3,"l1": tool.L1, "l2": tool.L2, "l3": tool.L3,
     "z": tool.z, "corRad": tool.cornerRadius, "chamfer": tool.chamfer, "toolType": tool.toolType, "id": tool.id,
        "neckAngle": tool.neckAngle, "centerCut": tool.centerCut, "coolantType": tool.coolantType, "threadTolerance": tool.threadTolerance,
        "threadPitch": tool.threadPitch, "mfr": tool.mfr, "mfrRef": tool.mfrRef, "mfrSecRef": tool.mfrSecRef, "code": tool.code,
        "codeBar": tool.codeBar, "comment": tool.comment
    }]).run()