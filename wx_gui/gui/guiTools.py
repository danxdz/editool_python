import wx, os

from tool import ToolsDefaultsData
from tool import ToolsCustomData

toolData = ToolsCustomData()
toolDefData = ToolsDefaultsData()


def load_masks():
    masks = toolDefData.tool_names_mask
    #check if the file exist
    check = os.path.isfile('toolsetup.txt')        
    if check:
        file = open('toolsetup.txt', 'r', encoding='utf-8')
        #read the data from the file
        masks = file.readlines()
        masks = [x.strip() for x in masks]

    else:
        file = open('toolsetup.txt', 'w', encoding='utf-8')
        #if file not exist create it and add some default data
        print("file not exist :: ", len(masks))
        for mask in masks:
            file.write(f"{mask}\n")
    file.close()        
    return masks

def toolDetailsPanel(self, tool):
    toolAttributes = tool.getAttributes()
    wids = []
    font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
    font_12 = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

    for key, value in toolAttributes.items():
        #print("key :: ", key, " :: ", value)
        # Create new label
        if value or value == 0:
            if key == 'D1' or key == 'D2' or key == 'D3' or key == 'L1' or key == 'L2' or key == 'L3' or key == 'z' or key == 'cornerRadius':
                self.tool_labels[key] = wx.StaticText(self,-1, label=str(value))
                self.tool_labels[key].SetFont(font)
                wids.append(self.tool_labels[key])
                #self.tool_labels[key].SetPosition((50, 250))

            if key == 'D1':
                print("key :: ", key, " :: ", value)
                self.tool_labels[key].SetFont(font_12)
                #self.tool_labels[key].SetPosition((300, 250))
            

    #add widgets to the sizer
    

    return wids




def on_change(self, event, label_text ):
        #get the value of the widget and the textbox name changed

        #print("change",label_text, event.GetString())
        #print("on_change :: ", self)
        tool = self.tool
       
        changedValue = event.GetString()

        if label_text == 'toolType':
            #get the index of the tool type
            changedValue = self.toolData.tool_types_list.index(changedValue)
            #print("changedValue :: ", changedValue)

        #set object attribute with the value of the widget
        setattr(tool, label_text, changedValue)   
        self.tool = tool





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

def add_line(self, tool):
        
    index = self.list_ctrl.GetItemCount()
    
    #print("adding tool line :: ", index, " :: ", tool.name)


    
    index = self.list_ctrl.InsertItem(index, str(index + 1))
    self.list_ctrl.SetItem(index, 1, str(tool.name))
    #set item background color
    self.list_ctrl.SetItemBackgroundColour(index, wx.Colour(255, 255, 255))
    self.list_ctrl.SetItem(index, 2, str(tool.D1))
    self.list_ctrl.SetItem(index, 3, str(tool.L1))
    self.list_ctrl.SetItem(index, 4, str(tool.D2))
    self.list_ctrl.SetItem(index, 5, str(tool.L2))
    self.list_ctrl.SetItem(index, 6, str(tool.D3))
    self.list_ctrl.SetItem(index, 7, str(tool.L3))
    self.list_ctrl.SetItem(index, 8, str(tool.z))
    self.list_ctrl.SetItem(index, 9, str(tool.cornerRadius))
    self.list_ctrl.SetItem(index, 10, str(tool.mfr))
    if tool.TSid:
        #print("tool.TSid :: ", tool.TSid)
        self.list_ctrl.SetItemBackgroundColour(index, wx.Colour(230, 250, 230))
    return index


def refreshToolList(self,tools, toolType):
    #print("refreshToolList :: tooltype :: ", toolType)
    #tools = load_tools_from_database(toolType)
    if tools:
        print("refreshToolList :: ", len(tools), " :: ", toolType)
    self.list_ctrl.DeleteAllItems()

    newToolTypeText = "all"
    if toolType != -1:
        newToolTypeText = self.toolData.tool_types_list[toolType] 
        print("refreshToolList :: ", newToolTypeText)     
    if tools:
        print(f"{len(tools)} tools loaded :: type : {newToolTypeText}")
        #self.list_ctrl.DeleteAllItems()
        for tool in tools:
            add_line(self, tool)
    else:
        print(f"no tools loaded :: type : {newToolTypeText}")
        #self.list_ctrl.DeleteAllItems()
    
    self.list_ctrl.Refresh()

def tooltypesButtons(self):
    self.iconsBar = wx.BoxSizer(wx.HORIZONTAL)
    #add buttons with tool types icons to the container
    #add first empty button
    self.bt = wx.BitmapButton(self, id=-1, bitmap=wx.Bitmap(f'icons/noFilter.png'), name="noFilter",style=wx.BORDER_RAISED)
    self.bt.SetToolTip(wx.ToolTip("no filter"))
    self.bt.SetBackgroundColour(wx.Colour(240, 240, 240))
    self.bt.SetWindowStyleFlag(wx.NO_BORDER)
    self.iconsBar.Add(self.bt, 0, wx.ALL, 5)
    self.Bind(wx.EVT_BUTTON, self.filterToolType, id=-1)
    if self.selected_toolType == -1:
        self.bt.Enabled = False
    else:
        self.bt.Enabled = True

    
    print("existent_tooltypes :: ", self.toolData.existent_tooltypes, self.selected_toolType)

    for i, toolType in enumerate(toolDefData.tool_types):

        #print("toolType :: ", toolType)
        icon = wx.Bitmap(f'icons/{toolType}.png')
        #set button size
        self.iconsBar.SetMinSize((20, 40))

        #add button to the container
        self.bt = wx.BitmapButton(self, id=i, bitmap=icon, name=toolType,style=wx.BORDER_RAISED)
        self.bt.SetToolTip(wx.ToolTip(toolType))
        self.bt.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.bt.SetWindowStyleFlag(wx.NO_BORDER)
        self.bt.Enabled = False
        self.iconsBar.Add(self.bt, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.filterToolType, id=i)
        if i in self.toolData.existent_tooltypes and i != self.selected_toolType:
           self.bt.Enabled = True

        

    #add the container to the main sizer
    return (self.iconsBar)



    

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