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
            tool = Tool(*tool_data[1:])
            tools_list.append(tool)
            print("tool added: ", tool.Name)
        return tools_list

def deleteTool(id):
    #connect to the database
    conn = sqlite3.connect('tool_manager.db')
    #create a cursor
    cursor = conn.cursor()
    #delete a record
    print("delete :: "+str(id.Name))
    tmp = "DELETE from tools WHERE name='" + str(id.Name) + "'"
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
        INSERT INTO tools (Name, toolType, GroupeMat, D1, L1, L2, L3, D3, NoTT, RayonBout, Chanfrein, CoupeCentre,
            ArrCentre, TypeTar, PasTar, Manuf, ManufRef, ManufRefSec, Code, CodeBar,Comment)
        VALUES (:Name, :toolType, :GroupeMat, :D1, :L1, :L2, :L3, :D3, :NoTT, :RayonBout, :Chanfrein, :CoupeCentre,
            :ArrCentre, :TypeTar, :PasTar, :Manuf, :ManufRef, :ManufRefSec, :Code, :CodeBar, :Comment)
    ''', tool.__dict__)

    conn.commit()

    print('Tool added to database.', tool.Name , conn.total_changes)

    conn.close()