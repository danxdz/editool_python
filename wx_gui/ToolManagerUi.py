import wx
import sys

import wx_gui.import_xml

class ToolManagerUI(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Tool Manager')
        self.panel = ToolPanel(self)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        open_xml = file_menu.Append(
            wx.ID_ANY, 'Open xml file', 
            'open a xml file with tool data'
        )
        open_zip = file_menu.Append(
            wx.ID_ANY, 'Open zip file', 
            'open a zip file with tool data'
        )
        exit = file_menu.Append(
            wx.ID_ANY, "exit", "close app"
        )
        menu_bar.Append(file_menu, '&File')
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_xml,
            source=open_xml,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_zip,
            source=open_zip,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.close_app,
            source=exit
        )
        self.SetMenuBar(menu_bar)

      
    def close_app(event, handle):
        print("exit",event.Title, handle, sep=" :: ")
        sys.exit()
        
    
    def on_open_xml(self, event):
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        wx_gui.import_xml.open_file( self, title,wcard)

    def on_open_zip(self, event):
        title = "Choose a Zip file:"
        wcard ="Zip files (*.zip)|*.zip"
        wx_gui.import_xml.open_file(self, title, wcard)

        


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

