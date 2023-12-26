from databaseTools import load_tools_from_database
from tool import Tool

def add_columns(self):
    self.list_ctrl.InsertColumn(0, "n" , width=30)
    self.list_ctrl.InsertColumn(1, 'name', width=100)
    self.list_ctrl.InsertColumn(2, 'D1', width=50)
    self.list_ctrl.InsertColumn(3, 'L1', width=50)
    self.list_ctrl.InsertColumn(4, 'D2', width=50)
    self.list_ctrl.InsertColumn(5, 'L2', width=50)
    self.list_ctrl.InsertColumn(6, 'D3', width=50)
    self.list_ctrl.InsertColumn(7, 'L3', width=50)
    self.list_ctrl.InsertColumn(8, 'Z', width=50)
    self.list_ctrl.InsertColumn(9, 'r', width=50)
    self.list_ctrl.InsertColumn(10, 'Manuf', width=100)
    self.list_ctrl.InsertColumn(11, 'eval', width=100)



import os

def getToolTypes():
    #get all tool types and ts models from getToolTypes txt file
    toolTypes = []
    tsModels = []

    with open("./wx_gui/tooltypes.txt", "r") as f:
        for line in f:
            #print(line)
            toolTypes.append(line.split(";")[1])
            #need to strip /n from end of line
            tsModels.append(line.split(";")[2].strip())
    
    return toolTypes, tsModels

def getToolTypesIcons(tooltypes, path):
    icons = []
    for tooltype in tooltypes:
        icon = path + tooltype + ".png"
        print("icon :: ", icon)
        icons.append(icon)
    return icons

def getToolTypesNumber(toolTypes, value): 
    for i, toolType in enumerate(toolTypes):
        if toolType == value:
            value = i
            return i
        
def refreshToolList(self, toolType):
    print("refreshToolList :: tooltype :: ", toolType)
    tools = load_tools_from_database(toolType)
    if tools:
        print(f"{len(tools)} tools loaded")
        self.list_ctrl.DeleteAllItems()
        for tool in tools:
            add_line(self, tool)
    else:
        print("no tools loaded")
        self.list_ctrl.DeleteAllItems()
    
    self.list_ctrl.Refresh()

def add_line(self, tool):
    index = self.list_ctrl.GetItemCount()

    self.fullToolsList[index] = tool

    #print("adding tool line :: ", index, " :: ", tool.Name)

    index = self.list_ctrl.InsertItem(index, str(index + 1))
    self.list_ctrl.SetItem(index, 1, str(tool.Name))
    self.list_ctrl.SetItem(index, 2, str(tool.D1))
    self.list_ctrl.SetItem(index, 3, str(tool.L1))
    self.list_ctrl.SetItem(index, 4, str(tool.D2))
    self.list_ctrl.SetItem(index, 5, str(tool.L2))
    self.list_ctrl.SetItem(index, 6, str(tool.D3))
    self.list_ctrl.SetItem(index, 7, str(tool.L3))
    self.list_ctrl.SetItem(index, 8, str(tool.NoTT))
    self.list_ctrl.SetItem(index, 9, str(tool.RayonBout))
    self.list_ctrl.SetItem(index, 10, str(tool.Manuf))

    return index

