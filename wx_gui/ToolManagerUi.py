import wx
import sys

import databaseTools as db
import import_xml_wx as iXml
import ts

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
            index = self.panel.add_line(tool)
            #self.tools_list.append(tool)
            self.panel.list_ctrl.Select(index)

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

        #enable alternating row colours
        #self.list_ctrl.EnableAlternateRowColours(enable=True)

        self.list_ctrl.Enable(True)

        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.get_focus, self.list_ctrl)
        self.list_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.right_click, self.list_ctrl)

        self.list_ctrl.InsertColumn(0, 'name', width=100)
        self.list_ctrl.InsertColumn(1, 'D1', width=50)
        self.list_ctrl.InsertColumn(2, 'L1', width=50)
        self.list_ctrl.InsertColumn(3, 'D2', width=50)
        self.list_ctrl.InsertColumn(4, 'L2', width=50)
        self.list_ctrl.InsertColumn(5, 'D3', width=50)
        self.list_ctrl.InsertColumn(6, 'L3', width=50)
        self.list_ctrl.InsertColumn(7, 'type', width=50)

        
   
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)        
        edit_button = wx.Button(self, label='Edit')
        edit_button.Bind(wx.EVT_BUTTON, self.on_menu_click)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)        
        self.SetSizer(main_sizer)

        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, "Create")
        self.popup_menu.Append(1, "Edit")
        self.popup_menu.Append(2, "Delete")
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=0)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=1)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=2)

        self.load_tools()

    def get_selected_item(self):
        index = self.list_ctrl.GetFirstSelected()
        print("index :: ", index)
        if index > -1:
            return self.row_obj_dict[index]
        else:
            return None

    def get_focus(self, event):
        ind = event.GetIndex()
        print ("GotFocus :: ",ind , " :: " , self.row_obj_dict[ind].Name)

    def right_click(self, event):
        count = self.list_ctrl.GetSelectedItemCount()
        #gets the position of the mouse click
        pos = self.list_ctrl.HitTest(event.GetPosition())

        if count < 2:
            #deselects all the items
            self.list_ctrl.Select(-1, 0)
            #selects the item clicked
            self.list_ctrl.Select(pos[0])

        #gets the index of the item clicked
        ind = self.list_ctrl.GetFirstSelected()
        print (ind)
        #gets the item clicked
        item = self.list_ctrl.GetItem(ind)
        
        print("RMC :: ",item,  " :: ", count , pos)

        self.show_popup(event)

    def add_line(self, tool):
        print("adding tool line :: ", tool.Name)
        index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), tool.Name)
        self.list_ctrl.SetItem(index, 1, str(tool.D1))
        self.list_ctrl.SetItem(index, 2, str(tool.L1))
        self.list_ctrl.SetItem(index, 3, str(tool.D2))
        self.list_ctrl.SetItem(index, 4, str(tool.L2))
        self.list_ctrl.SetItem(index, 5, str(tool.D3))
        self.list_ctrl.SetItem(index, 6, str(tool.L3))
        self.list_ctrl.SetItem(index, 7, str(tool.Type))
        self.row_obj_dict[index] = tool
        return index


    def create_tool(self, index):
        print("create tool :: ", self.row_obj_dict[index].Name)
        tool = self.row_obj_dict[index]
        
        #ts.conn()
        ts.copy_tool(tool)
        print("tool :: ", tool)

    def on_menu_click(self, event):
        id = event.GetId()
        print('in on_edit :: ', id)
        count = self.list_ctrl.GetSelectedItemCount()
        
        ind = self.list_ctrl.GetFirstSelected()
        print (ind)
        #gets the item clicked
        item = self.list_ctrl.GetItem(ind)
        
        print("EDIT :: ",item,  " :: ", count )

        print("count :: ", count)
        if count > 1:
            print("multiple items selected")
        else:
            print("single item selected")

        print("selected item :: ", self.get_selected_item())
        
        for i in range(count):
            self.list_ctrl.SetItemBackgroundColour(item=i+ind, col='#f0f2f0')
            self.list_ctrl.SetItemTextColour(item=i+ind, col='#000000')
            self.list_ctrl.RefreshItem(i+ind)
            self.create_tool(i+ind)
            

        if id == 0:
            print("Create")
        elif id == 1:
            print("Edit")
        elif id == 2:
            print("Delete")
            self.delete_selected_item()


    def load_tools(self):
        self.list_ctrl.ClearAll
        tools = db.load_tools_from_database(self)
        for tool in tools:
            self.add_line(tool)

    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)
