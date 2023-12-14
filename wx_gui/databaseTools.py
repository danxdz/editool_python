import sqlite3
from tool import Tool


def sqlConn():
    # Connect to the SQLite database
    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
    return cursor


def load_tools_from_database(self):
        cursor = sqlConn()
        cursor.execute("SELECT * FROM tools")
        tools = cursor.fetchall()
        print("tools readed from DB: ", len(tools))
        # add tools to list
        tools_list = []
        for tool_data in tools:
            tool = Tool(*tool_data[0:])
            tools_list.append(tool)
            print("tool added: ", tool.Name)
        return tools_list

def deleteTool(tool):
    #connect to the database
    conn = sqlite3.connect('tool_manager.db')
    #create a cursor
    cursor = conn.cursor()
    #delete a record
    print("delete :: "+str(tool.Name))
    tmp = "DELETE from tools WHERE id='" + str(tool.id) + "'"
    cursor.execute(tmp)
    #commit changes
    conn.commit()
    #close connection
    conn.close()


def saveTool(tool):
    # Connect to db or create it, if not exists
    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()

    # Create table 'tools' if not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            toolType TEXT,
            GroupeMat INT,
            D1 REAL,
            D2 REAL,
            D3 REAL,
            L1 REAL,
            L2 REAL,
            L3 REAL,
            NoTT INTEGER,
            RayonBout REAL,
            Chanfrein REAL,
            AngleDeg INTEGER,
            CoupeCentre TEXT,
            ArrCentre TEXT,
            TypeTar TEXT,
            PasTar REAL,
            Manuf TEXT,
            ManufRef TEXT,
            ManufRefSec TEXT,
            Code TEXT,
            CodeBar TEXT,
            Comment TEXT
        )
    ''')

    # Add tool into table 'tools'
    cursor.execute('''
        INSERT INTO tools (Name, toolType, GroupeMat, D1, L1, L2, L3, D3, NoTT, RayonBout, Chanfrein,AngleDeg, CoupeCentre,
            ArrCentre, TypeTar, PasTar, Manuf, ManufRef, ManufRefSec, Code, CodeBar,Comment)
        VALUES (:Name, :toolType, :GroupeMat, :D1, :L1, :L2, :L3, :D3, :NoTT, :RayonBout, :Chanfrein,:AngleDeg, :CoupeCentre,
            :ArrCentre, :TypeTar, :PasTar, :Manuf, :ManufRef, :ManufRefSec, :Code, :CodeBar, :Comment)
    ''', tool.__dict__)

    conn.commit()

    print('Tool added to database.', tool.Name , conn.total_changes)

    conn.close()

def update_tool(tool):
    #print all tool attributes
    for key, value in tool.getAttributes().items():
        print(key, value)

    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
    tmp = "UPDATE tools SET Name='" + str(tool.Name) + "', toolType='" + str(tool.toolType) + "', GroupeMat='" + str(tool.GroupeMat) + "', D1='" + str(tool.D1) + "', D2='" + str(tool.D2) +  "', L1='" + str(tool.L1) + "', L2='" + str(tool.L2) + "', L3='" + str(tool.L3) + "', D3='" + str(tool.D3) + "', NoTT='" + str(tool.NoTT) + "', RayonBout='" + str(tool.RayonBout) + "', Chanfrein='" + str(tool.Chanfrein) + "', AngleDeg='" + str(tool.AngleDeg) +  "', CoupeCentre='" + str(tool.CoupeCentre) + "', ArrCentre='" + str(tool.ArrCentre) + "', TypeTar='" + str(tool.TypeTar) + "', PasTar='" + str(tool.PasTar) + "', Manuf='" + str(tool.Manuf) + "', ManufRef='" + str(tool.ManufRef) + "', ManufRefSec='" + str(tool.ManufRefSec) + "', Code='" + str(tool.Code) + "', CodeBar='" + str(tool.CodeBar) + "', Comment='" + str(tool.Comment) + "' WHERE id='" + str(tool.id) + "'"
    print(tmp)
    cursor.execute(tmp)
    conn.commit()

    print('Tool updated in database.', tool.Name , "tool changed: ", conn.total_changes)
    conn.close()

