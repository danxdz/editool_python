import wx


#from tool_manager import ToolManagerUI


class ToolManagerUI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Tool Manager')
        self.panel = ToolPanel(self)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        open_folder_menu_item = file_menu.Append(
            wx.ID_ANY, 'Open xml file', 
            'open a xml file with tool data'
        )
        menu_bar.Append(file_menu, '&File')
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_xml,
            source=open_folder_menu_item,
        )
        self.SetMenuBar(menu_bar)

    def on_open_xml(self, event):
        title = "Choose a file:"
        dlg = wx.FileDialog(self, title, 
                           style=wx.DD_DEFAULT_STYLE,
                           wildcard="XML files (*.xml)|*.xml")
        if dlg.ShowModal() == wx.ID_OK:
            self.panel.update_tools_listing(dlg.GetPath())
        dlg.Destroy()


class ToolPanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.row_obj_dict = {}

        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, 100), 
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, 'name', width=140)
        self.list_ctrl.InsertColumn(1, 'D1', width=140)
        self.list_ctrl.InsertColumn(2, 'L1', width=200)
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)        
        edit_button = wx.Button(self, label='Edit')
        edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)        
        self.SetSizer(main_sizer)

    def on_edit(self, event):
        print('in on_edit')

    def update_tools_listing(self, folder_path):
        print(folder_path)



if __name__ == "__main__":
    app = wx.App()
    frame = ToolManagerUI()
    app.MainLoop()


