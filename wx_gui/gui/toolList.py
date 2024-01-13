
import wx

from importTools.validateImportDialogue import validateToolDialog

from gui.guiTools import add_columns
from gui.guiTools import refreshToolList
from gui.toolPreview import OnPaint

from databaseTools import delete_selected_item , load_tools_from_database

from ts import copy_tool, copy_holder, get_tool_TSid

from ObjectListView import ObjectListView, ColumnDefn

class ToolList(wx.Panel):    
    def __init__(self, parent, toolData):
        super().__init__(parent=parent)

        self.font_10 = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_name = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_tool_params_12 = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Courier 10 Pitch')
            
     

        self.parent = parent
        self.selected_tool = self.parent.toolData.selected_tool
        
        #initialize the tool list
        self.tool_labels = {}

        self.toolData = toolData
        if self.toolData.full_tools_list:
            self.selected_tool = self.toolData.full_tools_list[0]

        #create the sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        #this is the list control that will hold the tools list
        screenWidth, screenHeight = wx.GetDisplaySize()


        #get the columns for the list control from tool class

        simpleColumns = [
            ColumnDefn("Name", "left", 100, "name"),
            ColumnDefn("D1", "left", 50, "D1"),
            ColumnDefn("D2", "left", 50, "D2"),
            ColumnDefn("D3", "left", 50, "D3"),
            ColumnDefn("L1", "left", 50, "L1"),
            ColumnDefn("L2", "left", 50, "L2"),
            ColumnDefn("L3", "left", 50, "L3"),
            ColumnDefn("Z", "left", 50, "z"),
            ColumnDefn("Corner Radius", "left", 50, "cornerRadius"),
        ]
        
        self.dataObjects = self.toolData.full_tools_list
        self.olvSimple = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.olvSimple.SetColumns(simpleColumns)
        self.olvSimple.SetObjects(self.dataObjects)
        self.olvSimple.cellEditMode = ObjectListView.CELLEDIT_F2ONLY
        
        self.sizer.Add(self.olvSimple, 1, wx.ALL|wx.EXPAND, 5)

        #bind the events to the list control
        self.olvSimple.Bind(wx.EVT_LIST_ITEM_SELECTED, self.toolSelected, self.olvSimple, id=wx.ID_ANY)
        #right click event
        self.olvSimple.Bind(wx.EVT_RIGHT_DOWN, self.right_click, self.olvSimple)
        #double left click event
        self.olvSimple.Bind(wx.EVT_LEFT_DCLICK, self.db_click, self.olvSimple)





        self.toolView = wx.Panel(self, size=(int(screenWidth/3), int(screenHeight/5)))
        self.sizer.Add(self.toolView, 0, wx.ALL | wx.CENTER, 5)
        #need to bind the paint event to the panel
        self.toolView.Bind(wx.EVT_PAINT, self.OnPaint)

        
   
        '''
        #bind the events to the list control
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.toolSelected, self.list_ctrl, id=wx.ID_ANY)
        #right click event
        self.list_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.right_click, self.list_ctrl)
        #double left click event
        self.list_ctrl.Bind(wx.EVT_LEFT_DCLICK, self.db_click, self.list_ctrl)

        add_columns(self)'''

        
        refreshToolList(self,self.toolData)
        if toolData.full_tools_list:
            if len(toolData.full_tools_list) > 0:
                tool = toolData.full_tools_list[0]
   
        


        
        #create popup menu
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, "Create tool")
        self.popup_menu.Append(1, "Create tool with holder")
        self.popup_menu.Append(2, "Edit")
        self.popup_menu.Append(3, "Delete")
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(4, "Export")
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)


    def OnPaint(self, event):        
        tool = self.selected_tool
        #print("OnPaint", tool.name)
        dc = wx.PaintDC(self.toolView)
        if tool:
            OnPaint(self, dc, tool)


    def toolSelected(self, event):
        #get the selected tool

        tool = self.olvSimple.GetSelectedObject()
                  
        self.parent.statusBar.SetStatusText(f"tool selected: {tool.name} :: {tool.toolType}")

        if tool.name:
            print ("tool selected: ", tool.name , " :: ", tool.toolType)
            self.Refresh()
            self.selected_tool = tool           
        else:
            print("error :: tool selected:: ", tool)  

       
    def db_click(self, event):
        print("edit tool: ", self.olvSimple.GetSelectedObject().name)

        tool = self.olvSimple.GetSelectedObject()

        #EditDialog(self,tool, self.toolData.tool_types_list).ShowModal()
        validateToolDialog(self, tool, False).ShowModal()


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
            modif_tooltype = -1
            if count > 1:
                modif_tooltype = self.toolData.full_tools_list[i+ind].toolType

            if id == 0:                
                print("floatMenu :: Create")      
                #create tool :: false = no holder 
                print("create tool :: ", self.toolData.full_tools_list[i+ind].name)
                copy_tool(self, self.toolData.full_tools_list[i+ind], False)
                self.toolData.full_tools_list, existent_tooltypes = load_tools_from_database(self.toolData.full_tools_list[i+ind].toolType)
                 
            if id == 1:                
                print("floatMenu ::  Create with holder")     
                #create tool :: true = holder
                print("create holder for :: ", self.toolData.full_tools_list[i+ind].name)
                #id = ts.get_tool_TSid(tool)
                copy_holder(None, get_tool_TSid(self.toolData.full_tools_list[i+ind]))
            elif id == 2:
                print("floatMenu :: Edit :: ", self.toolData.full_tools_list[i+ind].name )
                validateToolDialog(self, self.toolData.full_tools_list[i+ind],False).ShowModal()
            elif id == 3:
                print("floatMenu :: Delete")
                delete_selected_item(self.GetParent(),i+ind)
            
        
        refreshToolList(self,self.toolData )


    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)