import wx

from importTools.validateImportDialogue import validateToolDialog

from gui.guiTools import refreshToolList

from gui.toolPreview import OnPaint

from databaseTools import delete_selected_item , load_tools_from_database

from ObjectListView3 import ObjectListView, ColumnDefn

import logging

from tool import ToolsDefaultsData

from gui.vp import OpenGLCanvas
#from gui.pyopengl_demo import MyPanel

import math


class ToolList(wx.Panel):    
    def __init__(self, parent, gl):
        super().__init__(parent)
        
        self.started = False

        self.font_10 = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_name = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_tool_params_12 = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Courier 10 Pitch')
            
        self.units = 1 #1 = mm, 0 = cm

        self.lang = parent.lang #0 = en, 1 = fr, 2 = pt
        self.ts = parent.ts
        self.menu = parent.menu
        # menu text
        #self.menus[menu][self.lang]
        self.create_tool = f"{self.menu.menus['createTool'][self.lang].capitalize()}"
                              
        self.clone_tool = f"{self.menu.menus['duplicate'][self.lang].capitalize()} {self.menu.menus['tool'][self.lang]}"
                    

        self.parent = parent
        self.toolData = self.parent.toolData
        self.selected_tool = self.toolData.selected_tool
        
        self.sort = True

        self.gl = gl



        #create the sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        #make a box to hold the drop boxs
        self.box = wx.BoxSizer(wx.HORIZONTAL)

        #add drop box to filter the tools, fill the drop box with the tool D1, make it unique
        #need to make something to make it for all the D1 d2 d3 L1 L2 L3 Z cornerRadius 
        self.filters = [['D1', 0, 0], ['D2', 0, 0], ['D3', 0, 0], ['L1', 0, 0], ['L2', 0, 0], ['L3', 0, 0], ['z', 0, 0], ['cornerRadius', 0, 0], ['TSid', 0, 0]]
        
        self.filters_dropbox = []    
        self.filtered_tools = self.toolData.full_tools_list
        
        #create the drop box within a loop but create an index for each drop box
        for index, filter in enumerate(self.filters):
            tool_data = self.getToolData(filter[0])
            #create the drop box
            self.filters_dropbox.append(wx.ComboBox(self, -1, choices=tool_data, style=wx.CB_READONLY))
            self.filters_dropbox[index].SetSelection(0)
            #bind the drop box to the event and pass the index of the drop box
            self.filters_dropbox[index].Bind(wx.EVT_COMBOBOX, lambda event, index=index: self.on_tool_data_change(event,index))
            self.filters_dropbox[index].SetFont(self.font_10)
            #add box to hold the drop box and the label
            self.tab = wx.BoxSizer(wx.VERTICAL)
            self.tab.Add(wx.StaticText(self, -1, filter[0]), 0, wx.ALL|wx.LEFT, 5)
            #add the drop box to the box
            self.tab.Add(self.filters_dropbox[index], 0, wx.ALL|wx.LEFT, 5)
            #add the box to the main box
            self.box.Add(self.tab, 0, wx.ALL|wx.EXPAND, 5)


        self.sizer.Add(self.box, 0, wx.ALL|wx.EXPAND, 5)


        """
        self.toolsD1 = self.getToolsD1(self.toolData.full_tools_list)
        #create the drop box
        self.toolType = wx.ComboBox(self, -1, choices=self.toolsD1, style=wx.CB_READONLY)
        self.toolType.SetSelection(0)
        self.toolType.Bind(wx.EVT_COMBOBOX, self.on_tool_d1_change)
        self.toolType.SetFont(self.font_10)
        self.sizer.Add(self.toolType, 0, wx.ALL|wx.EXPAND, 5)
"""

        #this is the list control that will hold the tools list
        self.screenWidth, self.screenHeight = wx.GetDisplaySize()

        #initialize the tool list
        self.tool_labels = {}

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
            ColumnDefn("Name", "left", 100, "name"),
            ColumnDefn("D1", "left", 50, "D1"),
            ColumnDefn("D2", "left", 50, "D2"),
            ColumnDefn("D3", "left", 50, "D3"),
            ColumnDefn("L1", "left", 50, "L1"),
            ColumnDefn("L2", "left", 50, "L2"),
            ColumnDefn("L3", "left", 50, "L3"),
            ColumnDefn("Z", "left", 50, "z"),
            ColumnDefn("Corner Radius", "left", 50, "cornerRadius"),
            ColumnDefn("TSid", "left", 50, "TSid"),
        ]
            #ColumnDefn("Holder", "left", 50, "holder"),
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
        #check if the tool have tsid

        self.popup_menu.Append(0, f'{self.menu.menus["open"][self.lang].capitalize()} {self.menu.menus["tool"][self.lang]}')
        self.popup_menu.Append(1, self.create_tool)
        self.popup_menu.Append(2, f"{self.menu.menus['createToolWithHolder'][self.lang].capitalize()}")                                   
        self.popup_menu.Append(3, f"{self.menu.menus['edit'][self.lang].capitalize()}")                                     
        #self.popup_menu.Append(4, f"{menu.get_menu('duplicate').capitalize()}")
        self.popup_menu.Append(5, f"{self.menu.menus['delete'][self.lang].capitalize()}")
        self.popup_menu.AppendSeparator()
        #self.popup_menu.Append(4, "Export")
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)
        
        #2d preview of the tool
        #self.toolView = wx.Panel(self, size=(int(self.screenWidth/3), int(self.screenHeight/5)))
        #self.sizer.Add(self.toolView, 1, wx.EXPAND, border=5)
        #self.toolView.Bind(wx.EVT_PAINT, self._OnPaint)

        #add radio buttons to select the units
        self.units_box = wx.BoxSizer(wx.HORIZONTAL)
        self.mm = wx.RadioButton(self, -1, 'mm', style=wx.RB_GROUP)
        self.mm.SetValue(True)
        self.mm.Bind(wx.EVT_RADIOBUTTON, self.on_units_change)
        self.mm.SetFont(self.font_10)
        self.units_box.Add(self.mm, 0, wx.ALL|wx.EXPAND, 5)
        self.cm = wx.RadioButton(self, -1, 'cm')
        self.cm.Bind(wx.EVT_RADIOBUTTON, self.on_units_change)
        self.cm.SetFont(self.font_10)
        self.units_box.Add(self.cm, 0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(self.units_box, 0, wx.ALL|wx.EXPAND, 5)

        #add a slider to change the size of the tool preview, can have step 1
        if self.toolData.selected_tool is not None:
            if self.toolData.selected_tool.L2:
                l2 = int(self.toolData.selected_tool.L2)
            else :
                l2 = int(self.toolData.selected_tool.L1)
            l3 = int(self.toolData.selected_tool.L3 - self.toolData.selected_tool.D3)
        else:
            l2 = 0
            l3 = 2
        # l2 cant be greater than l3
        if l2 >= l3:
            l2 = l3-2
            l3 =  l3+2 ## need to check this

        self.tool_slider = wx.Slider(self, -1, l2+2, l2, l3, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        #need to change slider min and max values
        
   
        self.tool_slider.Bind(wx.EVT_SLIDER, self.on_slider_change)
        self.sizer.Add(self.tool_slider, 0, wx.ALL|wx.EXPAND, 5)


        #3d preview of the tool
        gl_canvas = OpenGLCanvas(self, self.gl)
        self.sizer.Add(gl_canvas, 1, wx.EXPAND)


        #need to check list items and change the color of the line if the tool have tsid
        self.checkToolsTSid(self.olvSimple)
        
        refreshToolList(self, self.toolData)

        self.started = True

    def on_slider_change(self, event):
        #get the value of the slider
        value = self.tool_slider.GetValue()
        #change the color of the slider if to close to the max value, gets red
        if value >= (self.tool_slider.GetMax() - self.toolData.selected_tool.D3):
            self.tool_slider.SetForegroundColour(wx.RED)
        else:
            self.tool_slider.SetForegroundColour(wx.BLACK)
        self.Refresh()

    def on_units_change(self, event):
        if self.mm.GetValue():
            self.units = 1
        else:
            self.units = 0
        self.Refresh()
    
    def getToolData(self, filter, tools=None):
        data = []
        data.append("-") # make 1s value "-" to be the first value in the list so the user can select it to show all the tools
        if tools is None:
            tools = self.toolData.full_tools_list
        for tool in tools:
            value = getattr(tool, filter) # the filter is the key of the tool object
            value = str(value) # convert the value to string to be able to add it to the list
            if value not in data:
                data.append(value)
        return data
    

    def on_tool_data_change(self, event, index):
        if self.started is False:
            return      
        #get the index of the selected filter
        filter_value = self.filters_dropbox[index].GetValue()
        self.filters[index][1] = filter_value
        if filter_value == "-":
            self.filters[index][2] = 0
        else:
            self.filters[index][2] = 1
        logging.info("filters :: %s :: %s", self.filters, index)
        #filter the tools list by the selected filters, if many filters are selected, the index will be the last selected filter
        #and need to remove the filter if the user select the "-" value 
        #create a list to hold the tools filtered
        tools = []
        #get the tools list
        tools = self.filtered_tools
        #filter the tools list ; enumerate the filters list to get the index of the selected filter
        for i, filter in enumerate(self.filters):
            if filter[2] != 0:                
                tools = [tool for tool in tools if str(getattr(tool, str(self.filters[i][0]))) == filter[1]]
        
        #self.filtered_tools = tools
        
        #refresh the list
        self.olvSimple.SetObjects(tools)
        #select the first tool
        self.olvSimple.Select(0)
        #refresh the cb filters
        for i in range(len(self.filters_dropbox)):
            if i > index:
                self.filters_dropbox[i].SetItems(self.getToolData(self.filters[i][0], self.filtered_tools))
                self.filters_dropbox[i].SetSelection(0)

        

    
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
            #self.Refresh()

            #check if  int(self.toolData.selected_tool.L2) is int and round it up


            if self.toolData.selected_tool.L2:
                l2 = int(math.ceil(self.toolData.selected_tool.L2))
            else:
                l2 = int(math.ceil(self.toolData.selected_tool.L1)) 
            l3 = int(math.ceil(self.toolData.selected_tool.L3 - self.toolData.selected_tool.D3))
            
            self.tool_slider.SetMin(l2)
            self.tool_slider.SetValue(l2+2)
            self.tool_slider.SetMax(l3)

            if tool.TSid:
                self.parent.statusBar.SetStatusText(f"tool selected: {tool.name} :: {tooltype} :: TSid: {tool.TSid}")
                # get right click menu button addToHolder
                self.popup_menu.Enable(2, True)
                self.popup_menu.Enable(0, True)
                # change the create tool button text
                self.popup_menu.SetLabel(1, self.clone_tool)
                #
            else:
                self.parent.statusBar.SetStatusText(f"tool selected: {tool.name} :: {tooltype}")
                # get right click menu button addToHolder
                self.popup_menu.Enable(2, False)
                self.popup_menu.Enable(0, False)
                # change the create tool button text
                self.popup_menu.SetLabel(1, self.create_tool)
                

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
            print("floatMenu :: Open")
            #open tool
            print("open tool :: ", tool.name)
            self.ts.open_file(tool.TSid)
        elif id == 1:                
            print("floatMenu :: Create")      
            #create tool :: false = no holder 
            print("create tool :: ", tool.name)
            self.ts.copy_tool(self, tool, False, False)
        elif id == 2:                
            print("floatMenu ::  Insert into holder")     
            #create tool :: true = holder
            print("insert into holder for :: ", tool.name)
            logging.info("insert into holder for :: %s", tool.name)
            #id = ts.get_tool_TSid(tool)
            #copy_holder(self, tool)
            self.ts.insert_into_holder(tool)
        elif id == 3:
            print("floatMenu :: Edit :: ", tool.name )
            validateToolDialog(self, tool, False).ShowModal()
        elif id == 5:
            print("floatMenu :: Delete")
            self.olvSimple.RemoveObject(tool)
            delete_selected_item(self.GetParent(),tool)
        elif id == 5:
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




