import databaseTools as db


def delete_selected_item(self):
    index = self.getSelectedTool()
    print("INDEX :: ",index)
    index = self.list_ctrl.GetFirstSelected()
    print("INDEX :: ",index)

    print("deleting tool :: ", index, " :: ", self.row_obj_dict[index].Name)
    db.deleteTool(self.row_obj_dict[index])
    self.list_ctrl.DeleteItem(index)
    del self.row_obj_dict[index]


def load_tools(self):
    self.list_ctrl.ClearAll
    tools = db.load_tools_from_database(self)

    tools = reversed(tools)

    self.D1_cb.Append(str(" "))
    self.L1_cb.Append(str(" "))
    self.L2_cb.Append(str(" "))
    self.Z_cb.Append(str(" "))

    for tool in tools:
        self.add_line(tool)

        dropbox = self.D1_cb
        self.fill_dropboxs(tool.D1, dropbox)    
        dropbox = self.L1_cb
        self.fill_dropboxs(tool.L1, dropbox)
        dropbox = self.L2_cb
        self.fill_dropboxs(tool.L2, dropbox)
        dropbox = self.Z_cb
        self.fill_dropboxs(tool.NoTT, dropbox)