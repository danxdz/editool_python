import sqlite3
from tool import Tool
from gui.menus_inter import MenusInter
import logging

def sqlConn():
    # Connect to the SQLite database
    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
    return cursor



def load_tools_from_database(toolType, lang):
   
        #get the menu text from the dictionary
        menu = MenusInter(lang)
        #TODO return tools list by toolType
        
        cursor = sqlConn()
        try:
            #print("load_tools_from_database :: toolType :: ", toolType)
            if toolType == str(-1) or toolType == -1:
                cursor.execute("SELECT * FROM tools ORDER by D1 ASC")
            else:
                cursor.execute("SELECT * FROM tools WHERE toolType = ? ORDER by D1 ASC", (toolType,))
            tools = cursor.fetchall()
            # add tools to list
            tools_list = []
            existent_tooltypes = []
            for tool_data in tools:
                tool = Tool(*tool_data[0:])
                #create a list of tooltypes, add a new tooltype if not exists
                if tool.toolType not in existent_tooltypes:
                    existent_tooltypes.append(tool.toolType)
                tools_list.append(tool)
                        
            print(f"INFO :: {menu.get_menu('tools_readed_db').capitalize()} :: {len(tools_list)} :: {len(existent_tooltypes)}")
            
            return tools_list, existent_tooltypes
        
        except Exception as e:
            #create_db()
            print("Error loading tools from db: ", e)
            return [], []

def deleteTool(tool):
    if tool: 
        #connect to the database
        conn = sqlite3.connect('tool_manager.db')
        #create a cursor
        cursor = conn.cursor()
        #delete a record
        tmp = "DELETE from tools WHERE id='" + str(tool.id) + "'"
        cursor.execute(tmp)
        #commit changes
        conn.commit()
        #close connection
        conn.close()
        print(f":: deleted from database :: {tool.name} :: {tool.toolType}")


def delete_selected_item(self, tool):
    
    #delete tool from database
    deleteTool(tool)




def saveTool(tool, toolTypes):
    print("saveTool :: ",tool.id, tool.name, tool.toolType)
    if tool.id != 0: #filter for new tool #TODO: remove this filter
        update_tool(tool)
        return
    
    # Connect to db or create it, if not exists
    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
  
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS tools (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT,
            toolType    INT,
            cuttingMaterial TEXT,
            toolMaterial TEXT,
            D1          REAL,
            D2          REAL,
            D3          REAL,
            L1          REAL,
            L2          REAL,
            L3          REAL,
            z        INTEGER,
            cornerRadius   REAL,
            chamfer   REAL,
            neckAngle    REAL,
            centerCut TEXT,
            coolantType   TEXT,
            threadTolerance TEXT,
            threadPitch REAL,
            mfr       TEXT,
            mfrRef    TEXT,
            mfrSecRef TEXT,
            code        TEXT,
            codeBar     TEXT,
            comment     TEXT,
            TSid        TEXT
        )
    ''')


    # Add tool into table 'tools'
    cursor.execute('''
        INSERT INTO tools (name, toolType, cuttingMaterial, toolMaterial, D1, L1, D2, L2, L3, D3, z, cornerRadius, chamfer,neckAngle, centerCut,
            coolantType, threadTolerance, threadPitch, mfr, mfrRef, mfrSecRef, code, codebar, comment, TSid)
        VALUES (:name, :toolType, :cuttingMaterial, :toolMaterial, :D1, :L1, :D2, :L2, :L3, :D3, :z, :cornerRadius, :chamfer,:neckAngle, :centerCut,
            :coolantType, :threadTolerance, :threadPitch, :mfr, :mfrRef, :mfrSecRef, :code, :codeBar, :comment, :TSid)
    ''', tool.__dict__)

    conn.commit()

    print('Tool added to database.', tool.name , toolTypes[int(tool.toolType)], "changed: " ,  conn.total_changes)

    #get the last added tool id
    cursor.execute("SELECT id FROM tools ORDER BY id DESC LIMIT 1")
    tool.id = cursor.fetchone()[0]
    print("last added tool id :: ", tool.id)
 
    conn.close()

def update_tool(tool):
    #print all tool attributes
    #for key, value in tool.getAttributes().items():
    #   print(key, value)

    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
    tmp = "UPDATE tools SET name='" + str(tool.name) + "', toolType='" + str(tool.toolType) + "', cuttingMaterial='" + str(tool.cuttingMaterial) + "', toolMaterial='" + str(tool.toolMaterial) + "', D1='" + str(tool.D1) + "', D2='" + str(tool.D2) +  "', L1='" + str(tool.L1) + "', L2='" + str(tool.L2) + "', L3='" + str(tool.L3) + "', D3='" + str(tool.D3) + "', z='" + str(tool.z) + "', cornerRadius='" + str(tool.cornerRadius) + "', chamfer='" + str(tool.chamfer) + "', neckAngle='" + str(tool.neckAngle) +  "', centerCut='" + str(tool.centerCut) + "', coolantType='" + str(tool.coolantType) + "', threadTolerance='" + str(tool.threadTolerance) + "', threadPitch='" + str(tool.threadPitch) + "', mfr='" + str(tool.mfr) + "', mfrRef='" + str(tool.mfrRef) + "', mfrSecRef='" + str(tool.mfrSecRef) + "', Code='" + str(tool.code) + "', codeBar='" + str(tool.codeBar) + "', comment='" + str(tool.comment) + "', TSid='" + str(tool.TSid) + "' WHERE id='" + str(tool.id) + "'"
    #print(tmp)
    cursor.execute(tmp)
    conn.commit()

    logging.info(f'Tool updated in database. {tool.name} tools changed: {conn.total_changes}')
    #print('Tool updated in database.', tool.name , "tool changed: ", conn.total_changes)
    
    conn.close()

