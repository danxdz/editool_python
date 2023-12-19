
import wx
from gui.editDialog import EditDialog

from gui.guiTools import add_columns

from databaseTools import delete_selected_item
from databaseTools import add_line


import databaseTools as db


import ts

class ToolList(wx.Panel):    
    def __init__(self, parent, main_frame):
        super().__init__(parent)
        self.main_frame = main_frame
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.fullToolsList = {}
        self.toolType =  parent.toolTypes[parent.toolType]

        #this is the list control that will hold the tools list
        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, 300), 
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )   
   
        #this is needed to allow the lines oflist control to be selected
        self.list_ctrl.Enable(True)

        #bind the events to the list control
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.toolSelected, self.list_ctrl, id=wx.ID_ANY)
        #right click event
        self.list_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.right_click, self.list_ctrl)
        #double left click event
        self.list_ctrl.Bind(wx.EVT_LEFT_DCLICK, self.db_click, self.list_ctrl)

        add_columns(self)
        
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)        

        #create comboboxes
        self.cb_contrainer = wx.BoxSizer(wx.HORIZONTAL)

        self.D1_cb = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.cb_contrainer.Add(self.D1_cb, 0, wx.ALL | wx.CENTER, 5)

        self.L1_cb = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.cb_contrainer.Add(self.L1_cb, 0, wx.ALL | wx.CENTER, 5)

        self.L2_cb = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.cb_contrainer.Add(self.L2_cb, 0, wx.ALL | wx.CENTER, 5)
        
        self.Z_cb = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.cb_contrainer.Add(self.Z_cb, 0, wx.ALL | wx.CENTER, 5)

        main_sizer.Add(self.cb_contrainer, 0, wx.ALL | wx.CENTER, 5)
        
        self.D1_cb.Bind(wx.EVT_COMBOBOX, lambda event: self.on_select(event, self.filter_D1,"D1", self.L1_cb, self.L2_cb, self.Z_cb))
        self.L1_cb.Bind(wx.EVT_COMBOBOX, lambda event: self.on_select(event, self.filter_L1,"L1", self.L2_cb, self.Z_cb))


        edit_button = wx.Button(self, label='Edit')
        edit_button.Bind(wx.EVT_BUTTON, self.on_menu_click)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)      

        self.SetSizer(main_sizer)   

        #create popup menu
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, "Create")
        self.popup_menu.Append(1, "Edit")
        self.popup_menu.Append(2, "Delete")
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(3, "Export")
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=0)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=1)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=2)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=3)

    


    def on_select(self, event, filter_func, filter, *dropboxes):
        print("on_select :: "  + event.GetString() +  " :: " +  filter )
        self.list_ctrl.ClearAll()
        self.add_columns()
        for dropbox in dropboxes:
            dropbox.Clear()

        new_tool_list = []
        if event.GetString() == " ": # blank
            value = 0
        else:
            value = float(event.GetString())

        print(" ********************************* value :: ", value)
        for tool in self.fullToolsList.values():
            if value == 0:  # blank
                print("empty value :: ", value)
                add_line(self,tool)
                new_tool_list.append(tool)
            else:
                print("value :: ", value , " :: ", tool.D1)
                if filter == "D1":
                    flt = tool.D1
                elif filter == "L1":
                    flt = tool.L1
                if (flt == value):
                    print("adding tool :: ", tool.Name)
                    filter_func(tool,value)
                    add_line(tool)
                    new_tool_list.append(tool)

        for tool in new_tool_list:
            print("filter func: ", filter_func)
            filter_func(tool,value)

        # Após aplicar todos os filtros, atualize a lista
        self.list_ctrl.Refresh() 

    def filter_D1(self, tool, value):
            self.fill_dropboxs(tool.L1, self.L1_cb)
            self.fill_dropboxs(tool.L2, self.L2_cb)
            self.fill_dropboxs(tool.NoTT, self.Z_cb)

    def filter_L1(self, tool, value):
            self.fill_dropboxs(tool.D1, self.D1_cb)
            self.fill_dropboxs(tool.L2, self.L2_cb)
            self.fill_dropboxs(tool.NoTT, self.Z_cb)


 

    def toolSelected(self, event):
        tool = self.list_ctrl.GetFirstSelected()
        try :
            print ("tool selected: ", tool.Name )
        except AttributeError:
            print("tool selected:: ", tool)


       
    def db_click(self, event):
        #print("edit tool: ", self.getSelectedTool().Name)
        EditDialog(self, self.fullToolsList[self.list_ctrl.GetFirstSelected()], self.toolType).ShowModal()

    def right_click(self, event):
        count = self.list_ctrl.GetSelectedItemCount()
        #gets the position of the mouse click
        pos = self.list_ctrl.HitTest(event.GetPosition())

        if count < 2:
            #deselects all the items
            self.list_ctrl.Select(-1, 0)
            #selects the item clicked
            self.list_ctrl.Select(pos[0])       

        self.show_popup(event)

    def fill_dropboxs(self, tool, dropbox):
        #add the D1 value to the dropbox if it is not already there
        items = dropbox.GetItems()
        d1 = str(tool)
        if str(d1) not in items:
            #print(d1, " :: " , items)
            dropbox.Append(d1)

        #order the dropbox items remeber they are strings, so make sure to convert to real numbers
        items = dropbox.GetItems()
        #print("items :: ", items)
        #first item must be blank we dont want to sort that
        if items[0] == " ":
            items.pop(0)
        #print("items :: ", items)
        items.sort(key=float)
        #append the blank item back to the list to make it the first item
        items.insert(0, " ")
        
        dropbox.SetItems(items)
        #print("items :: ", items)





    def create_tool(self, index):
        print("create tool :: ", self.fullToolsList[index].Name)
        tool = self.fullToolsList[index]
        
        #ts.conn()
        ts.copy_tool(tool)
        print("tool :: ", tool.Name, " created")

    def on_menu_click(self, event):
        id = event.GetId()        
        print('on_menu_click :: ', id)


        count = self.list_ctrl.GetSelectedItemCount()        
        ind = self.list_ctrl.GetFirstSelected()

        if count > 1:
            print("multiple items selected")
            for i in range(count):
                print("selected item :: ")
        else:
            print("single item selected")


        for i in range(count):
            if id == 0:                
                print("Create")           
                self.create_tool(i+ind)
            elif id == 1:
                print("Edit :: ", self.fullToolsList[i+ind].Name )
                EditDialog(self, self.fullToolsList[i+ind], self.toolType ).ShowModal()
            elif id == 2:
                print("Delete")
                toolType = self.fullToolsList[i+ind].toolType
                delete_selected_item(self.GetParent(),i+ind, toolType) 


    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)


