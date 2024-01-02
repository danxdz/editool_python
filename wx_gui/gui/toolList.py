
import wx

from importTools.validateImportDialogue import validateToolDialog

from gui.guiTools import add_columns
from gui.guiTools import refreshToolList
from databaseTools import delete_selected_item

import ts

class ToolList(wx.Panel):    
    def __init__(self, parent, toolData):
        super().__init__(parent)

        self.parent = parent
        
        #initialize the tool list
       
        self.toolData = toolData

        #this is the list control that will hold the tools list
        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, -1), 
            style=wx.LC_REPORT | wx.BORDER_SIMPLE
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

    

    def toolSelected(self, event):
        tool = self.toolData.fullToolsList[self.list_ctrl.GetFirstSelected()]  
        toolTypeName = self.toolData.toolTypesList[tool.toolType]           
        self.parent.statusBar.SetStatusText(f"tool selected: {self.list_ctrl.GetFirstSelected()} :: {tool.name} :: {toolTypeName}")

        try :
            print ("tool selected: ", tool.name , " :: ", toolTypeName )
        except AttributeError:
            print("error :: tool selected:: ", tool)

       
    def db_click(self, event):
        print("edit tool: ",  self.list_ctrl.GetFirstSelected())
        i = self.list_ctrl.GetFirstSelected()

        tool = self.toolData.fullToolsList[i]

        #EditDialog(self,tool, self.toolData.toolTypesList).ShowModal()
        validateToolDialog(self, tool).ShowModal()
      


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



    def create_tool(self, index, holder): #holder = true or false
        print("create tool :: ", self.toolData.fullToolsList[index].name)
        tool = self.toolData.fullToolsList[index]

        #check if tool is created
        if tool.TSid == "" or tool.TSid == None:
            ts.copy_tool(tool, holder)
            print("tool :: ", tool.name, " created")
        else:
            if holder:
                print("tool  ", tool.name, " already created ", tool.TSid)
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
                print("floatMenu :: Edit :: ", self.toolData.fullToolsList[i+ind].name )
                validateToolDialog(self, self.toolData.fullToolsList[i+ind]).ShowModal()
            elif id == 3:
                print("floatMenu :: Delete")
                delete_selected_item(self.GetParent(),i+ind) 
                self.list_ctrl.DeleteAllItems()
                self.toolData.fullToolsList = refreshToolList(self, -1)


    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)