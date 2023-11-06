import wx
import sys

import databaseTools as db
import import_xml_wx as iXml


class ToolManagerUI(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Tool Manager')
        self.panel = ToolPanel(self, self)
        self.create_menu()
        self.SetSize(800, 800)
        self.Centre()
        self.Show()

        self.tools_list = []

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
        tool = iXml.open_file(self, title, wcard)
        print("tool %s", tool)
        if tool:
            print("Tool added:", tool.Name)
            self.panel.add_line(tool)


    def on_open_zip(self, event):
        title = "Choose a Zip file:"
        wcard ="Zip files (*.zip)|*.zip"
        iXml.open_file(self, title, wcard)

        


class ToolPanel(wx.Panel):    
    def __init__(self, parent, main_frame):
        super().__init__(parent)
        self.main_frame = main_frame


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.row_obj_dict = {}

        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, 300), 
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.EnableAlternateRowColours = True

        self.list_ctrl.InsertColumn(0, 'name', width=100)
        self.list_ctrl.InsertColumn(1, 'D1', width=50)
        self.list_ctrl.InsertColumn(2, 'L1', width=50)
        
   
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)        
        edit_button = wx.Button(self, label='Edit')
        edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)        
        self.SetSizer(main_sizer)

        self.load_tools()

    def on_plot(self, event):
        ind = event.GetIndex()
        print("type: ", event)
        print (ind)
        print (self.row_obj_dict[ind].Name)

    def add_line(self, tool):
        print("adding tool line :: ", tool.Name)
        index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), tool.Name)
        self.list_ctrl.SetItem(index, 1, str(tool.D1))
        self.list_ctrl.SetItem(index, 2, str(tool.L1))
        self.row_obj_dict[index] = tool
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_plot, self.list_ctrl)


    def on_edit(self, event):
        print('in on_edit')

    def load_tools(self):
        self.list_ctrl.ClearAll
        tools = db.load_tools_from_database(self)
        for tool in tools:
            self.add_line(tool)
