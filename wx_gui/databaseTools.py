import sqlite3
from tool import Tool

import os

def getToolTypes():
    #read folder with icons to get tool types
    iconPath = "icons/"
    iconFiles = os.listdir(iconPath)
    i=0
    toolTypes = []
    for iconFile in iconFiles:
        if os.path.isfile(iconPath+iconFile):
            #print(iconFile)                  
            i += 1
            name = iconFile.split(".")[0]
            name = name.split("-")[1]
            #print(name)
            toolTypes.append(name)

    return toolTypes

def sqlConn():
    # Connect to the SQLite database
    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
    return cursor


def add_line(self, tool):
    index = self.panel.list_ctrl.GetItemCount()

    self.panel.fullToolsList[index] = tool

    #print("adding tool line :: ", index, " :: ", tool.Name)

    index = self.panel.list_ctrl.InsertItem(index, str(index + 1))
    self.panel.list_ctrl.SetItem(index, 1, str(tool.Name))
    self.panel.list_ctrl.SetItem(index, 2, str(tool.D1))
    self.panel.list_ctrl.SetItem(index, 3, str(tool.L1))
    self.panel.list_ctrl.SetItem(index, 4, str(tool.D2))
    self.panel.list_ctrl.SetItem(index, 5, str(tool.L2))
    self.panel.list_ctrl.SetItem(index, 6, str(tool.D3))
    self.panel.list_ctrl.SetItem(index, 7, str(tool.L3))
    self.panel.list_ctrl.SetItem(index, 8, str(tool.NoTT))
    self.panel.list_ctrl.SetItem(index, 9, str(tool.RayonBout))
    self.panel.list_ctrl.SetItem(index, 10, str(tool.Manuf))

    return index

def load_tools_from_database(self,toolType):
        cursor = sqlConn()
        try:
            #print("load_tools_from_database :: toolType :: ", toolType)
            if toolType == str(0) or toolType == 0:
                cursor.execute("SELECT * FROM tools ORDER by D1 ASC")
            else:
                cursor.execute("SELECT * FROM tools WHERE toolType = ? ORDER by D1 ASC", (toolType,))
            tools = cursor.fetchall()
            #print("tools readed from DB: ", len(tools))
            # add tools to list
            tools_list = []
            for tool_data in tools:
                tool = Tool(*tool_data[0:])
                tools_list.append(tool)
                #print("tool added: ", tool.Name)

            self.panel.list_ctrl.DeleteAllItems()

            if tools is None:
                return "no tools found"
                        
            #tools = reversed(tools) #reverse list to get last added tool first

            #add " " (empty) to dropboxs to clear selection
            
            self.panel.D1_cb.Append(str(" "))
            self.panel.L1_cb.Append(str(" "))
            self.panel.L2_cb.Append(str(" "))
            self.panel.Z_cb.Append(str(" "))

            for tool in tools_list:
                #print("tool :: ", tool.Name, " :: ", tool.toolType, " :: ", toolType)
                #if toolType == "0" or str(toolType) == str(tool.toolType):
                add_line(self, tool)

                #dropbox = self.D1_cb
                #self.fill_dropboxs(tool.D1, dropbox)    
                #dropbox = self.L1_cb
                #self.fill_dropboxs(tool.L1, dropbox)
                #dropbox = self.L2_cb
                #self.fill_dropboxs(tool.L2, dropbox)
                #dropbox = self.Z_cb
                #self.fill_dropboxs(tool.NoTT, dropbox)

            self.panel.list_ctrl.Refresh()

            return len(tools_list)
        
        except Exception as e:
            #create_db()
            print("Error: ", e)

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


def delete_selected_item(self, index, toolType):
    
    print("deleting tool :: ", index, " :: ", self.panel.fullToolsList[index].Name, " toolType :: ", toolType)

    deleteTool(self.panel.fullToolsList[index])

    #self.list_ctrl.DeleteItem(index)

    del self.panel.fullToolsList[index]

    self.panel.list_ctrl.DeleteAllItems()
    tools = load_tools_from_database(self, toolType)
    print("tools loaded :: ", tools)


def saveTool(tool):
    # Connect to db or create it, if not exists
    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
  
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS tools (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            Name        TEXT,
            toolType    INT    REFERENCES editool_tooltype (id) ON DELETE NO ACTION
                                                                ON UPDATE NO ACTION
                                                                MATCH SIMPLE,
            GroupeMat   INT,
            D1          REAL,
            D2          REAL,
            D3          REAL,
            L1          REAL,
            L2          REAL,
            L3          REAL,
            NoTT        INTEGER,
            RayonBout   REAL,
            Chanfrein   REAL,
            AngleDeg    INTEGER,
            CoupeCentre TEXT,
            ArrCentre   TEXT,
            threadTolerance TEXT,
            threadPitch REAL,
            Manuf       TEXT,
            ManufRef    TEXT,
            ManufRefSec TEXT,
            Code        TEXT,
            CodeBar     TEXT,
            Comment     TEXT,
            CuttingMaterial TEXT,
            TSid        TEXT
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS editool_tooltype (
            id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            toolType VARCHAR (100) NOT NULL
            )
    ''')

    #get all tool types from getToolTypes
    toolTypes = getToolTypes()

    toolTypeText = toolTypes[int(tool.toolType)]

    cursor.execute("SELECT * FROM editool_tooltype WHERE toolType = ?", (toolTypeText,))
    
    tool_types = cursor.fetchone()

    print("tool_types found on db :: ", tool_types,  tool.toolType, toolTypes[int(tool.toolType)] )

    if tool_types:
        if tool_types[1] == tool.toolType:
            tool.toolType = tool_types[0] 
            print("tool_type exist ", tool.toolType, tool_types[1]) 
    else:
        print("toolTypes to write :: ", toolTypes)
         #get the array index of the tool type
        test = []
        for i, toolType in enumerate(toolTypes):
            #print(i, toolType)
            test.append((i+1, toolType))
        #print("test :: ", test)
        #print("toolTypes :: ", toolTypes)
        try:
            cursor.executemany("INSERT INTO editool_tooltype (id, toolType) VALUES(?,?)", test)
            conn.commit()

        except Exception as ex:
            print("error: ", ex)


    # Add tool into table 'tools'
    cursor.execute('''
        INSERT INTO tools (Name, toolType, GroupeMat, D1, L1, D2, L2, L3, D3, NoTT, RayonBout, Chanfrein,AngleDeg, CoupeCentre,
            ArrCentre, threadTolerance, threadPitch, Manuf, ManufRef, ManufRefSec, Code, CodeBar,Comment, CuttingMaterial, TSid)
        VALUES (:Name, :toolType, :GroupeMat, :D1, :L1, :D2, :L2, :L3, :D3, :NoTT, :RayonBout, :Chanfrein,:AngleDeg, :CoupeCentre,
            :ArrCentre, :threadTolerance, :threadPitch, :Manuf, :ManufRef, :ManufRefSec, :Code, :CodeBar, :Comment, :CuttingMaterial, :TSid)
    ''', tool.__dict__)

    conn.commit()

    print('Tool added to database.', tool.Name , toolTypes[int(tool.toolType)], "changed: " ,  conn.total_changes)
 
    conn.close()

def update_tool(tool):
    #print all tool attributes
    #for key, value in tool.getAttributes().items():
    #   print(key, value)

    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
    tmp = "UPDATE tools SET Name='" + str(tool.Name) + "', toolType='" + str(tool.toolType) + "', GroupeMat='" + str(tool.GroupeMat) + "', D1='" + str(tool.D1) + "', D2='" + str(tool.D2) +  "', L1='" + str(tool.L1) + "', L2='" + str(tool.L2) + "', L3='" + str(tool.L3) + "', D3='" + str(tool.D3) + "', NoTT='" + str(tool.NoTT) + "', RayonBout='" + str(tool.RayonBout) + "', Chanfrein='" + str(tool.Chanfrein) + "', AngleDeg='" + str(tool.AngleDeg) +  "', CoupeCentre='" + str(tool.CoupeCentre) + "', ArrCentre='" + str(tool.ArrCentre) + "', threadTolerance='" + str(tool.threadTolerance) + "', threadPitch='" + str(tool.threadPitch) + "', Manuf='" + str(tool.Manuf) + "', ManufRef='" + str(tool.ManufRef) + "', ManufRefSec='" + str(tool.ManufRefSec) + "', Code='" + str(tool.Code) + "', CodeBar='" + str(tool.CodeBar) + "', Comment='" + str(tool.Comment) + "', CuttingMaterial='" + str(tool.CuttingMaterial) + "', TSid='" + str(tool.TSid) + "' WHERE id='" + str(tool.id) + "'"
    print(tmp)
    cursor.execute(tmp)
    conn.commit()

    print('Tool updated in database.', tool.Name , "tool changed: ", conn.total_changes)
    conn.close()

