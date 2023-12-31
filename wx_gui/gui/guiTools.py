from databaseTools import load_tools_from_database

import wx



#TODO: add columns to config

def add_columns(self):
    self.list_ctrl.InsertColumn(0, "n" , width=30)
    self.list_ctrl.InsertColumn(1, 'name', width=100)
    self.list_ctrl.InsertColumn(2, 'D1', width=50)
    self.list_ctrl.InsertColumn(3, 'L1', width=50)
    self.list_ctrl.InsertColumn(4, 'D2', width=50)
    self.list_ctrl.InsertColumn(5, 'L2', width=50)
    self.list_ctrl.InsertColumn(6, 'D3', width=50)
    self.list_ctrl.InsertColumn(7, 'L3', width=50)
    self.list_ctrl.InsertColumn(8, 'Z', width=50)
    self.list_ctrl.InsertColumn(9, 'r', width=50)
    self.list_ctrl.InsertColumn(10, 'Manuf', width=100)
    self.list_ctrl.InsertColumn(11, 'eval', width=100)



def getToolTypesIcons(tooltypes, path):
    icons = []
    for tooltype in tooltypes:
        icon = path + tooltype + ".png"
        print("icon :: ", icon)
        icons.append(icon)
    return icons

def getToolTypesNumber(toolTypes, value): 
    for i, toolType in enumerate(toolTypes):
        #print("getToolTypesNumber :: ", toolType, " :: ", value)
        if toolType == value:
            value = i
            #print("getToolTypesNumber :: ", toolType, " :: ", value, i)

            return i
        
def refreshToolList(self, toolType):
    #print("refreshToolList :: tooltype :: ", toolType)

    tools = load_tools_from_database(toolType)

    newToolTypeText = "all"
    if toolType != -1:
        newToolTypeText = self.toolData.toolTypesList[toolType]
       
    if tools:
        print(f"{len(tools)} tools loaded :: type : {newToolTypeText}")

        self.list_ctrl.DeleteAllItems()
        for tool in tools:
            add_line(self, tool)
    else:
        print(f"no tools loaded :: type : {newToolTypeText}")
        self.list_ctrl.DeleteAllItems()
    
    self.list_ctrl.Refresh()
    return tools

def add_line(self, tool):
    index = self.list_ctrl.GetItemCount()
    print("adding tool line :: ", index, " :: ", tool.Name)

    self.toolData.fullToolsList.append(tool)


    index = self.list_ctrl.InsertItem(index, str(index + 1))
    self.list_ctrl.SetItem(index, 1, str(tool.Name))
    self.list_ctrl.SetItem(index, 2, str(tool.D1))
    self.list_ctrl.SetItem(index, 3, str(tool.L1))
    self.list_ctrl.SetItem(index, 4, str(tool.D2))
    self.list_ctrl.SetItem(index, 5, str(tool.L2))
    self.list_ctrl.SetItem(index, 6, str(tool.D3))
    self.list_ctrl.SetItem(index, 7, str(tool.L3))
    self.list_ctrl.SetItem(index, 8, str(tool.NoTT))
    self.list_ctrl.SetItem(index, 9, str(tool.RayonBout))
    self.list_ctrl.SetItem(index, 10, str(tool.Manuf))

    return index


def tooltypesButtons(self):
    self.iconsBar = wx.BoxSizer(wx.HORIZONTAL)
    #add buttons with tool types icons to the container
    #add first empty button
    self.bt = wx.BitmapButton(self, id=-1, bitmap=wx.Bitmap(f'icons/noFilter.png'), name="noFilter",style=wx.BORDER_RAISED)
    self.bt.SetToolTip(wx.ToolTip("no filter"))
    self.iconsBar.Add(self.bt, 0, wx.ALL, 5)
    self.Bind(wx.EVT_BUTTON, self.filterToolType, id=-1)
    

    for i, toolType in enumerate(self.toolData.toolTypesList):
        #print("toolType :: ", toolType)
        icon = wx.Bitmap(f'icons/{toolType}.png')
        #set button size
        self.iconsBar.SetMinSize((20, 40))
        #add button to the container
        self.bt = wx.BitmapButton(self, id=i, bitmap=icon, name=toolType,style=wx.BORDER_RAISED)
        self.bt.SetToolTip(wx.ToolTip(toolType))
        self.iconsBar.Add(self.bt, 0, wx.ALL, 5)
        #set tooltip for each button
        self.Bind(wx.EVT_BUTTON, self.filterToolType, id=i)

    #add the container to the main sizer
    self.main_sizer.Add(self.iconsBar, 0, wx.ALL, 5)
    self.SetSizer(self.main_sizer)
    self.SetAutoLayout(1)
    self.main_sizer.Fit(self)


def create_menu(self):

    # add file menu
    file_menu = wx.Menu()

    open_xml = file_menu.Append(
        wx.ID_ANY, 'Open xml file', 
        'open a xml file with tool data'
    )        
    self.Bind(
        event=wx.EVT_MENU, 
        handler=self.on_open_xml,
        source=open_xml,
    )

    ISO13999 = file_menu.Append(
        wx.ID_ANY, 'Paste tool ISO13999', 
        'paste tool data ISO13999'
    )        
    self.Bind(
        event=wx.EVT_MENU, 
        handler=self.on_paste_iso13999,
        source=ISO13999,
    )

    open_zip = file_menu.Append(
        wx.ID_ANY, 'Open zip file', 
        'open a zip file with tool data'
    )        
    self.Bind(
        event=wx.EVT_MENU, 
        handler=self.on_open_zip,
        source=open_zip,
    )

    exp_xml = file_menu.Append(
        wx.ID_ANY, 'Export XML file', 
        'export tool data into XML file'
    )
    self.Bind(
        event=wx.EVT_MENU, 
        handler=self.on_export_xml,
        source=exp_xml,
    )

    exit = file_menu.Append(
        wx.ID_ANY, "exit", "close app"
    )
    self.Bind(
        event=wx.EVT_MENU,
        handler=self.close_app,
        source=exit
    )

    # add file menu to menu bar
    
    menu_bar = wx.MenuBar()
    menu_bar.Append(file_menu, '&File')

    # add tools config menu
    config = wx.Menu()
    toolSetup = config.Append(
        wx.ID_ANY, 'Tool Setup', 
        'setup tool data'
    )
    self.Bind(
        event=wx.EVT_MENU,
        handler=self.toolSetupPanel,
        source=toolSetup
    )
    menu_bar.Append(config, '&Config')

    # add holders config menu
    holdersConfig = config.Append(
        wx.ID_ANY, 'Holders', 
        'setup holder data'
    )        
    self.Bind(
        event=wx.EVT_MENU,
        handler=self.HoldersSetupPanel,
        source=holdersConfig
    )


    self.SetMenuBar(menu_bar)