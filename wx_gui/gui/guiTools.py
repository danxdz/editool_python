import databaseTools as db


def delete_selected_item(self, toolType):
    index = self.getSelectedTool()
    print("INDEX :: ",index)
    index = self.list_ctrl.GetFirstSelected()
    print("INDEX :: ",index)

    print("deleting tool :: ", index, " :: ", self.fullToolsList[index].Name)
    db.deleteTool(self.fullToolsList[index])
    self.list_ctrl.DeleteItem(index)
    del self.fullToolsList[index]
    self.list_ctrl.DeleteAllItems()
    load_tools(self,toolType)



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
    self.list_ctrl.SetItem(index, 10, str(tool.toolType))
    self.list_ctrl.SetItem(index, 11, str(tool.Manuf))

    return index

def load_tools(self, toolType):
    print("loading tools", self)
    self.list_ctrl.DeleteAllItems()

    tools = db.load_tools_from_database(self)

    if tools is None:
        return
    
    print("tooltype :: ", toolType)



    #tools = reversed(tools) #reverse list to get last added tool first

    #add " " (empty) to dropboxs to clear selection
    self.D1_cb.Append(str(" "))
    self.L1_cb.Append(str(" "))
    self.L2_cb.Append(str(" "))
    self.Z_cb.Append(str(" "))

    for tool in tools:
        if toolType == "" or toolType == tool.toolType:
            add_line(self, tool)

        #dropbox = self.D1_cb
        #self.fill_dropboxs(tool.D1, dropbox)    
        #dropbox = self.L1_cb
        #self.fill_dropboxs(tool.L1, dropbox)
        #dropbox = self.L2_cb
        #self.fill_dropboxs(tool.L2, dropbox)
        #dropbox = self.Z_cb
        #self.fill_dropboxs(tool.NoTT, dropbox)

    self.list_ctrl.Refresh()