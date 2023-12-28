
import wx
from gui.editDialog import EditDialog

from gui.guiTools import add_columns
from gui.guiTools import refreshToolList
from gui.guiTools import add_line

from databaseTools import delete_selected_item

import ts

class ToolList(wx.Panel):    
    def __init__(self, parent, toolData):
        super().__init__(parent)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        #initialize the tool list
        self.fullToolsList = {}

        self.toolData = toolData

        self.toolTypesList = toolData.toolTypes

        self.tsModelsList = toolData.tsModels

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

        self.list_ctrl.Fit()
        
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)    

        self.SetSizer(main_sizer)   

        #create popup menu
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, "Create tool")
        self.popup_menu.Append(1, "Create tool with holder")
        self.popup_menu.Append(2, "Edit")
        self.popup_menu.Append(3, "Delete")
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(4, "Export")
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)

        #load tools from database to list control   
        refreshToolList(self,-1)


    def toolSelected(self, event):
        tool = self.list_ctrl.GetFirstSelected()
        try :
            print ("tool selected: ", tool.Name )
        except AttributeError:
            print("tool selected:: ", tool)

       
    def db_click(self, event):
        #print("edit tool: ", self.getSelectedTool().Name)

        tool =  self.fullToolsList[self.list_ctrl.GetFirstSelected()]         

        EditDialog(self,tool, self.toolTypesList,self.tsModelsList).ShowModal()

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


    def create_tool(self, index, holder): #holder = true or false
        print("create tool :: ", self.fullToolsList[index].Name)
        tool = self.fullToolsList[index]

        #check if tool is created
        if tool.TSid == "" or tool.TSid == None:
            ts.copy_tool(tool, holder, self.tsModelsList)
            print("tool :: ", tool.Name, " created")
        else:
            if holder:
                print("tool  ", tool.Name, " already created ", tool.TSid)
                id = ts.get_tool_TSid(tool)
                ts.copy_holder(None, id)
            else:
                resp = wx.MessageBox('tool already created, retry?', 'Warning', wx.YES_NO | wx.ICON_QUESTION)  #TODO: add a dialog to select if recreate or not

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
                print("floatMenu :: Create")      
                #create tool :: false = no holder     
                self.create_tool(i+ind, False)
            if id == 1:                
                print("floatMenu ::  Create with holder")     
                #create tool :: true = holder
                self.create_tool(i+ind, True)
            elif id == 2:
                print("floatMenu :: Edit :: ", self.fullToolsList[i+ind].Name )
                EditDialog(self, self.fullToolsList[i+ind], self.toolTypesList,self.tsModelsList ).ShowModal()
            elif id == 3:
                print("floatMenu :: Delete")
                toolType = self.fullToolsList[i+ind].toolType
                delete_selected_item(self.GetParent(),i+ind, toolType) 
                self.list_ctrl.DeleteAllItems()
                refreshToolList(self, toolType)


    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)