
import wx

from importTools.validateImportDialogue import validateToolDialog

from gui.guiTools import refreshToolList
from gui.toolPreview import OnPaint

from databaseTools import delete_selected_item , load_tools_from_database

from ts import copy_tool, copy_holder

from ObjectListView import ObjectListView, ColumnDefn

from gui.menus_inter import MenusInter


class ToolList(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.font_10 = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_name = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_tool_params_12 = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Courier 10 Pitch')
            
        self.lang = parent.lang #0 = en, 1 = fr, 2 = pt
        self.ts = parent.ts
       

        #get the menu text from the dictionary
        menu = MenusInter(self.lang)

        self.parent = parent
        self.toolData = self.parent.toolData
        self.selected_tool = self.toolData.selected_tool
        
        #initialize the tool list
        self.tool_labels = {}


        #create the sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        #this is the list control that will hold the tools list
        screenWidth, screenHeight = wx.GetDisplaySize()

        #get the columns for the list control from tool class

        self.imageListSmall = wx.ImageList(40, 20)
        
        self.olvSimple = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        musicImageIndex = self.olvSimple.AddNamedImages('endMill', "icons/endMill.png")
        self.olvSimple.AddNamedImages('ballMill', "icons/ballMill.png")
        self.olvSimple.AddNamedImages('radiusMill', "icons/radiusMill.png")
        self.olvSimple.AddNamedImages('chamferMill', "icons/chamferMill.png")
        self.olvSimple.AddNamedImages('tslotMill', "icons/tslotMill.png")

        if self.toolData.full_tools_list != []:
            #add the images to the list control
            self.olvSimple.SetImageList(self.imageListSmall, wx.IMAGE_LIST_SMALL)
            #set the 1st column to be the image column

            simpleColumns = [
                ColumnDefn("TS", "center", 50, musicImageIndex),

                ColumnDefn("Name", "left", 100, "name"),
                ColumnDefn("D1", "left", 50, "D1"),
                ColumnDefn("D2", "left", 50, "D2"),
                ColumnDefn("D3", "left", 50, "D3"),
                ColumnDefn("L1", "left", 50, "L1"),
                ColumnDefn("L2", "left", 50, "L2"),
                ColumnDefn("L3", "left", 50, "L3"),
                ColumnDefn("Z", "left", 50, "z"),
                ColumnDefn("Corner Radius", "left", 50, "cornerRadius"),
                ColumnDefn("Holder", "left", 50, "holder"),
                ColumnDefn("TSid", "left", 50, "TSid"),
            ]
            self.olvSimple.SetColumns(simpleColumns)
            #self.olvSimple.CreateCheckStateColumn(0)
            self.olvSimple.SetObjects(self.toolData.full_tools_list)


            #self.olvSimple.cellEditMode = ObjectListView.CELLEDIT_F2ONLY
            
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

            refreshToolList(self, self.toolData)

            #create popup menu
            self.popup_menu = wx.Menu()
            self.popup_menu.Append(0, f"{menu.get_menu('create').capitalize()} {menu.get_menu('tool')}")
            self.popup_menu.Append(1, f"{menu.get_menu('createToolWithHolder').capitalize()}")
            self.popup_menu.Append(2, f"{menu.get_menu('edit').capitalize()}")
            self.popup_menu.Append(5, f"{menu.get_menu('duplicate').capitalize()}")
            self.popup_menu.Append(3, f"{menu.get_menu('delete').capitalize()}")
            self.popup_menu.AppendSeparator()
            #self.popup_menu.Append(4, "Export")
            self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)

    def getTsImage(self, tool):
        #print("getTsImage :: ", tool.name)
        if tool.toolType == "endMill":
            return "endMill"
        elif tool.toolType == "ballMill":
            return "ballMill"
        elif tool.toolType == "radiusMill":
            return "radiusMill"
        elif tool.toolType == "chamferMill":
            return "chamferMill"
        elif tool.toolType == "tslotMill":
            return "tslotMill"
        

    def OnPaint(self, event):   
        #check if there is a any tool
        if len(self.toolData.full_tools_list) > 0:
            tool = self.selected_tool
            #print("OnPaint :: ", tool)
            #print("OnPaint", tool.name)
            dc = wx.PaintDC(self.toolView)
            if tool:
                OnPaint(self, dc, tool)


    def toolSelected(self, event):
        #get the selected tool or tools if multiple selected, get the first one
        tool  = self.olvSimple.GetSelectedObject() or self.olvSimple.GetSelectedObjects()[0]

        if tool:
            self.parent.statusBar.SetStatusText(f"tool selected: {tool.name} :: {tool.toolType}")
            self.parent.toolData.selected_tool = tool
            self.selected_tool = tool
            self.Refresh() 
                

    def db_click(self, event):
        print("edit tool: ", self.olvSimple.GetSelectedObject().name)

        tool = self.olvSimple.GetSelectedObject()

        #EditDialog(self,tool, self.toolData.tool_types_list).ShowModal()
        validateToolDialog(self, tool, False).ShowModal()


    def right_click(self, event):

        index = self.olvSimple.GetIndexOf(self.olvSimple.GetSelectedObject())  
        self.show_popup(event)


    def on_menu_click(self, event):
        id = event.GetId()        
        print('on_menu_click :: ', id)

        count = self.olvSimple.GetSelectedItemCount()      
        ind = self.olvSimple.GetFirstSelected()


    
        if count > 1:
            print("multiple items selected")
            tools = self.olvSimple.GetSelectedObjects()
            for tool in tools:
                self.selectOption(tool, id)

        else:
            print("single item selected")
            tool = self.olvSimple.GetSelectedObject()
            self.selectOption(tool, id)

         

    def selectOption(self, tool, id):
        if id == 0:                
            print("floatMenu :: Create")      
            #create tool :: false = no holder 
            print("create tool :: ", tool.name)
            copy_tool(self, tool, False, False)
                
        if id == 1:                
            print("floatMenu ::  Create with holder")     
            #create tool :: true = holder
            print("create holder for :: ", tool.name)
            #id = ts.get_tool_TSid(tool)
            #copy_holder(self, tool)
            print (self.ts.insert_into_holder(tool))

        elif id == 2:
            print("floatMenu :: Edit :: ", tool.name )
            validateToolDialog(self, tool, False).ShowModal()
        elif id == 3:
            print("floatMenu :: Delete")
            delete_selected_item(self.GetParent(),tool)
        elif id == 4:
            msg = "not implemented yet"
            #alertbox that will show the message
            dlg = wx.MessageDialog(self, msg, "Export tool", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()

        elif id == 5:
            print("floatMenu :: Duplicate")
            copy_tool(self, tool, False, True)
        
        self.toolData.full_tools_list, existent_tooltypes = load_tools_from_database(self.toolData.selected_toolType, self.lang)
        refreshToolList(self, self.toolData )

    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)