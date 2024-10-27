import wx

from importTools.validateImportDialogue import validateToolDialog

from gui.guiTools import refreshToolList

from gui.toolPreview import OnPaint

from databaseTools import delete_selected_item , load_tools_from_database

from ObjectListView import ObjectListView, ColumnDefn

from gui.menus_inter import MenusInter

import logging

from tool import ToolsDefaultsData

from gui.vp import OpenGLCanvas
#from gui.pyopengl_demo import MyPanel



class ToolList(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent)
            
        self.font_10 = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_name = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_tool_params_12 = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Courier 10 Pitch')
            
        self.lang = parent.lang #0 = en, 1 = fr, 2 = pt
        self.ts = parent.ts

        #get the menu text from the dictionary
        menu = MenusInter(self.lang)
        # menu text
        self.create_tool = f"{menu.get_menu('create').capitalize()} {menu.get_menu('tool')}"
        self.clone_tool = f"{menu.get_menu('duplicate').capitalize()} {menu.get_menu('tool')}"

        self.parent = parent
        self.toolData = self.parent.toolData
        self.selected_tool = self.toolData.selected_tool
        
        self.sort = True


        #initialize the tool list
        self.tool_labels = {}

        #create the sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        #this is the list control that will hold the tools list
        self.screenWidth, self.screenHeight = wx.GetDisplaySize()

        #get the columns for the list control from tool class
        self.olvSimple = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.olvSimple.SetEmptyListMsg("No tools found")
        self.olvSimple.SetEmptyListMsgFont(self.font_10)
        self.olvSimple.typingSearchesSortColumn = True
        
        '''        
        self.imageListSmall = wx.ImageList(20, 10)        
        self.olvSimple = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.olvSimple.AddNamedImages('ballMill', "icons/ballMill.png")
        self.olvSimple.AddNamedImages('radiusMill', "icons/radiusMill.png")
        self.olvSimple.AddNamedImages('chamferMill', "icons/chamferMill.png")
        self.olvSimple.AddNamedImages('tslotMill', "icons/tslotMill.png")
        self.olvSimple.AddNamedImages('endMill', "icons/endMill.png")
        self.olvSimple.SetImageList(self.imageListSmall, wx.IMAGE_LIST_SMALL)'''

        print("toolData :: ", self.olvSimple.GetObjects(), len(self.toolData.full_tools_list))

        
        simpleColumns = [
            ColumnDefn("TS", "center", 50, self.olvSimple),
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
        ]
            #ColumnDefn("TSid", "left", 50, "TSid"),
        self.olvSimple.SetColumns(simpleColumns)

        #self.olvSimple.CreateCheckStateColumn(0)

        if self.toolData.full_tools_list != []:
            
            self.olvSimple.SetObjects(self.toolData.full_tools_list)

            #self.olvSimple.cellEditMode = ObjectListView.CELLEDIT_F2ONLY
            self.olvSimple.CreateCheckStateColumn()
            #self.olvSimple.useAlternateBackColors = True
            # set the colors for the rows
            #self.olvSimple.oddRowsBackColor = wx.Colour(255, 255, 250) 
            #self.olvSimple.evenRowsBackColor = wx.Colour(240, 240, 250)
            self.olvSimple.oddRowsBackColor = wx.Colour(255, 255, 250) 
            self.olvSimple.evenRowsBackColor = wx.Colour(255, 255, 250)         
            
        self.sizer.Add(self.olvSimple, 1, wx.ALL|wx.EXPAND, 5)

        #bind the events to the list control
        self.olvSimple.Bind(wx.EVT_LIST_ITEM_SELECTED, self.toolSelected, self.olvSimple, id=wx.ID_ANY)
        #right click event
        self.olvSimple.Bind(wx.EVT_RIGHT_DOWN, self.right_click, self.olvSimple)
        #double left click event
        self.olvSimple.Bind(wx.EVT_LEFT_DCLICK, self.db_click, self.olvSimple)

        #get the bond evt when click the list header
        self.olvSimple.Bind(wx.EVT_LIST_COL_CLICK, self.on_sort)

        #create popup menu
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, self.create_tool)
        #check if the tool have tsid
        self.popup_menu.Append(1, f"{menu.get_menu('createToolWithHolder').capitalize()}")
        self.popup_menu.Append(2, f"{menu.get_menu('edit').capitalize()}")
        #self.popup_menu.Append(5, f"{menu.get_menu('duplicate').capitalize()}")
        self.popup_menu.Append(3, f"{menu.get_menu('delete').capitalize()}")
        self.popup_menu.AppendSeparator()
        #self.popup_menu.Append(4, "Export")
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)
        
        #2d preview of the tool

        #self.toolView = wx.Panel(self, size=(int(self.screenWidth/3), int(self.screenHeight/5)))
        #self.sizer.Add(self.toolView, 1, wx.EXPAND, border=5)
        #self.toolView.Bind(wx.EVT_PAINT, self._OnPaint)


        #3d preview of the tool
        #add scene to the panel
        #self.setScene()        
        canvas = OpenGLCanvas(self)
        self.sizer.Add(canvas, 1, wx.EXPAND)

        #grid with tool parameters
        self.toolParamsPanel = wx.Panel(self, size=(int(self.screenWidth/3), int(self.screenHeight/15)), style=wx.BORDER_SIMPLE)
        self.toolParamsPanel.SetBackgroundColour(wx.Colour(255, 255, 250))
        self.toolParamsPanel.SetFont(self.font_tool_params_12)
        #add textboxes to the panel
        self.toolParamsPanel.SetSizer(wx.GridSizer(1, 10, 5, 5))
        self.toolParamsPanel.GetSizer().Add(wx.StaticText(self.toolParamsPanel, label="D1"))
        self.toolParamsPanel.GetSizer().Add(wx.TextCtrl(self.toolParamsPanel, size=(50, 20)))
        self.toolParamsPanel.GetSizer().Add(wx.StaticText(self.toolParamsPanel, label="D2"))
        self.toolParamsPanel.GetSizer().Add(wx.TextCtrl(self.toolParamsPanel, size=(50, 20)))
        self.toolParamsPanel.GetSizer().Add(wx.StaticText(self.toolParamsPanel, label="D3"))
        self.toolParamsPanel.GetSizer().Add(wx.TextCtrl(self.toolParamsPanel, size=(50, 20)))
        self.toolParamsPanel.GetSizer().Add(wx.StaticText(self.toolParamsPanel, label="L1"))
        self.toolParamsPanel.GetSizer().Add(wx.TextCtrl(self.toolParamsPanel, size=(50, 20)))
        self.toolParamsPanel.GetSizer().Add(wx.StaticText(self.toolParamsPanel, label="L2"))
        self.toolParamsPanel.GetSizer().Add(wx.TextCtrl(self.toolParamsPanel, size=(50, 20)))


        self.sizer.Add(self.toolParamsPanel, 1, wx.EXPAND)


        #need to check list items and change the color of the line if the tool have tsid
        self.checkToolsTSid(self.olvSimple)
        
        refreshToolList(self, self.toolData)

    def checkToolsTSid(self, olvSimple):
        print("check")
                
    
    def on_sort(self, event):
        print("on_sort")
        #get the column name
        selected_column = event.GetColumn()
        print("col_name :: ", selected_column)
        #get the order of the column
        
        self.sort = not self.sort
        #sort the list
        self.olvSimple.SortBy(selected_column, self.sort)
        #refresh the list
        self.olvSimple.RefreshObjects(self.olvSimple.GetObjects())
        refreshToolList(self, self.toolData)


    def _OnPaint(self, event):
        #check if there is a any tool
        if len(self.toolData.full_tools_list) > 0:
            tool = self.selected_tool

            dc = wx.PaintDC(self.toolView)

            if tool:
                OnPaint(self, dc, tool)


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
        

    def toolSelected(self, event):
        #get the selected tool or tools if multiple selected, get the first one
        tool  = self.olvSimple.GetSelectedObject() or self.olvSimple.GetSelectedObjects()[0]

        if tool:
            # get tool type name

            tsd = ToolsDefaultsData()
            tooltype = tsd.tool_types[tool.toolType]

            self.parent.statusBar.SetStatusText(f"tool selected: {tool.name} :: {tooltype}")
            self.parent.toolData.selected_tool = tool
            self.selected_tool = tool
            self.Refresh()

            if tool.TSid:
                self.parent.statusBar.SetStatusText(f"tool selected: {tool.name} :: {tooltype} :: TSid: {tool.TSid}")
                # get right click menu button addToHolder
                self.popup_menu.Enable(1, True)
                # change the create tool button text
                self.popup_menu.SetLabel(0, self.clone_tool)
                #
            else:
                self.parent.statusBar.SetStatusText(f"tool selected: {tool.name} :: {tooltype}")
                # get right click menu button addToHolder
                self.popup_menu.Enable(1, False)
                # change the create tool button text
                self.popup_menu.SetLabel(0, self.create_tool)
                

    def db_click(self, event):
        print("edit tool: ", self.olvSimple.GetSelectedObject().name)

        tool = self.olvSimple.GetSelectedObject()

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
            self.ts.copy_tool(self, tool, False, False)
                
        if id == 1:                
            print("floatMenu ::  Insert into holder")     
            #create tool :: true = holder
            print("insert into holder for :: ", tool.name)
            logging.info("insert into holder for :: %s", tool.name)
            #id = ts.get_tool_TSid(tool)
            #copy_holder(self, tool)
            self.ts.insert_into_holder(tool)

        elif id == 2:
            print("floatMenu :: Edit :: ", tool.name )
            validateToolDialog(self, tool, False).ShowModal()
        elif id == 3:
            print("floatMenu :: Delete")
            self.olvSimple.RemoveObject(tool)
            delete_selected_item(self.GetParent(),tool)
        elif id == 4:
            msg = "not implemented yet"
            #alertbox that will show the message
            dlg = wx.MessageDialog(self, msg, "Open tool", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()

        elif id == 5:
            print("floatMenu :: Duplicate")
            #copy_tool(self, tool, False, True)
        
        self.toolData.full_tools_list, existent_tooltypes = load_tools_from_database(self.toolData.selected_toolType, self.lang)
        refreshToolList(self, self.toolData )

    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)




