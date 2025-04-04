import wx
import os
import logging

from tool import ToolsDefaultsData
from tool import ToolsCustomData

from gui.menus_inter import MenusInter

from databaseTools import load_tools_from_database

class FileDialogHandler:
    def __init__(self):
        pass

    def open_file_dialog(self, title, wCard):
        dlg = wx.FileDialog(self, title, 
                       wildcard=wCard, 
                       style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            file_path = dlg.GetPaths()
            dlg.Destroy()
            return file_path
        return None
    

class GenericMessageBox(wx.Dialog):
    def __init__(self, parent, text, title = ''):
        wx.Dialog.__init__(self, parent, -1, title = title, size = (360,140), style = wx.DEFAULT_DIALOG_STYLE)
        header_panel = wx.Panel(self, wx.ID_ANY, size = (360, 60), pos = (0,0))
        header_panel.SetBackgroundColour('#FFFFFF')
        label = wx.StaticText(header_panel, -1, text, pos = (20,20))        
        buttons_panel = wx.Panel(self, wx.ID_ANY, size = (500, 100), pos = (0, 50))
        #add sizer buttons
        sz = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(buttons_panel, wx.ID_OK, "duplicate", pos = (20, 15))
        bt2 = wx.Button(buttons_panel, wx.ID_YES, "update", pos = (120, 15))
        bt_cancel = wx.Button(buttons_panel, wx.ID_CANCEL, "cancel", pos = (250, 15))

        # disable the update button for now
        bt2.Enable(False)

        btn.SetDefault()

        # bind the buttons to the event
        self.Bind(wx.EVT_BUTTON, self.on_update, bt2)

        buttons_panel.SetSizer(sz)
        self.Center()
    
    def on_update(self, event):
        id = event.GetId()
        print("2 id :: ", id)
        self.Close()


        
toolData = ToolsCustomData()
toolDefData = ToolsDefaultsData()


def load_masks():
    '''load the masks from the file or from the default data'''
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



def add_line(panel, tool):
        
    index = panel.olvSimple.GetItemCount()
    
    #print("adding tool line :: ", index, " :: ", tool.name)
    
    index = panel.olvSimple.InsertItem(index, str(tool.TSid))
    #set one V if TSid exist

    panel.olvSimple.SetItem(index, 1, str(tool.name))
    #set item background color
    panel.olvSimple.SetItemBackgroundColour(index, wx.Colour(255, 255, 255))
    panel.olvSimple.SetItem(index, 2, str(tool.D1))
    panel.olvSimple.SetItem(index, 3, str(tool.L1))
    panel.olvSimple.SetItem(index, 4, str(tool.D2))
    panel.olvSimple.SetItem(index, 5, str(tool.L2))
    panel.olvSimple.SetItem(index, 6, str(tool.D3))
    panel.olvSimple.SetItem(index, 7, str(tool.L3))
    panel.olvSimple.SetItem(index, 8, str(tool.z))
    #panel.olvSimple.SetItem(index, 9, str(tool.cornerRadius))
    #panel.olvSimple.SetItem(index, 10, str(tool.mfr))
    if tool.TSid:
        #print("tool.TSid :: ", tool.TSid)
        panel.olvSimple.SetItemBackgroundColour(index, wx.Colour(230, 250, 230))
    return index


def refreshToolList(panel, toolData):
    selected = panel.olvSimple.GetSelectedObject()
    if selected:
        print("selected :: ", selected.name)
        parent = panel.GetParent()
        parent.selected_tool = selected
   
    tool_type = toolData.selected_toolType
    tools = toolData.full_tools_list
    
    new_tool_type_text = "all"
    if tool_type != -1:
        new_tool_type_text = toolData.tool_types_list[tool_type]
        
    if tools:
        print(f"INFO :: {len(tools)} tools loaded :: type : {new_tool_type_text}")
        panel.olvSimple.SetObjects(tools)
        panel.olvSimple.Refresh()
        
        tt = panel.olvSimple.GetObjects()
        col_count = panel.olvSimple.GetColumnCount()
        
        for i, tool in enumerate(tt):
            if tool.TSid:
                panel.olvSimple.SetItemBackgroundColour(i, wx.Colour(204, 250, 229))
                if col_count > 10:  # Only set column 10 if it exists
                    panel.olvSimple.SetItem(i, 10, "X")
            elif tool.imported:
                panel.olvSimple.SetItemBackgroundColour(i, wx.Colour(255, 255, 214))
                if col_count > 10:  # Only set column 10 if it exists
                    panel.olvSimple.SetItem(i, 10, " ")
    else:
        panel.olvSimple.SetObjects(tools)
        print(f"INFO :: no tools loaded :: type : {new_tool_type_text}")
    
    panel.Refresh()
    panel.Update()
    panel.Layout()

def tooltypesButtons(self):
    self.iconsBar = wx.BoxSizer(wx.HORIZONTAL)
    tool_icons = []

    #add buttons with tool types icons to the container
    #add first empty button
    self.bt = wx.BitmapButton(self, id=99, bitmap=wx.Bitmap('icons/noFilter.png'), name="noFilter",style=wx.BORDER_RAISED)
    self.bt.SetToolTip(wx.ToolTip("no filter"))
    self.bt.SetBackgroundColour(wx.Colour(240, 240, 240))
    self.bt.SetWindowStyleFlag(wx.NO_BORDER)
    #self.iconsBar.Add(self.bt, 0, wx.ALL, 5)
    self.bt.SetWindowStyleFlag(wx.BORDER_RAISED)

    self.Bind(wx.EVT_BUTTON, self.filterToolType, id=-1)
    tool_icons.append(self.bt)
    
    #print("existent_tooltypes :: ", self.toolData.existent_tooltypes, self.selected_toolType)

    for i, toolType in enumerate(toolDefData.tool_types):

        #print("toolType :: ", toolType)
        icon = wx.Bitmap(f'icons/{toolType}.png')
        #set button size
        #self.iconsBar.SetMinSize((20, 40))

        #add button to the container
        self.bt = wx.BitmapButton(self, id=i, bitmap=icon, name=toolType,style=wx.BORDER_RAISED)
        #get language text for the tool type
        menu = MenusInter(self.lang)
        toolType_inter = f"{menu.get_menu(toolType).capitalize()}"
        self.bt.SetToolTip(wx.ToolTip(toolType_inter))
        self.bt.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.bt.SetWindowStyleFlag(wx.NO_BORDER)
        self.bt.Enabled = False
        #self.iconsBar.Add(self.bt, 0, wx.ALL, 5)
        tool_icons.append(self.bt)
        self.Bind(wx.EVT_BUTTON, self.filterToolType, id=i)
        if i in self.toolData.existent_tooltypes and i != self.selected_toolType:
           self.bt.Enabled = True
        


    #add the container to the main sizer
    #return (self.iconsBar)
    return tool_icons


def get_custom_settings(self):

    lang = ''   

    #read the config file
    #if the file not exist create it and add the default language get from the ts
    config_exists = os.path.isfile('config.txt')
    if config_exists:
        file = open('config.txt', 'r', encoding='utf-8')
        #read all lines from the file
        lines = file.readlines()
        lines = [x.strip().split(";") for x in lines]
        #check if line is not empty
        if lines:
            for  line in lines:
                if line[0] == 'lang':
                    lang = line[1]
        file.close()
        
    elif lang == '':
        logging.warning('config file not exist')
        lang = self.ts.get_language()
        logging.info(f"ts current language :: {lang}")
        lang = lang.split('-')[0]
        MenusInter.set_lang(self,lang)
        
    logging.info(f"saved language :: {lang}")

    self.lang = lang
    


def build_menus(self):

    #update the language of the menus
    if (not self.lang) and self.lang != 0:
        self.lang = MenusInter.GetCustomLanguage()
    #get the menu text from the dictionary
    self.menu = MenusInter(self.lang)

    #for key, value in menu.menus.items():
    #    print("key :: ", key, " :: ", value)

    file_menu = wx.Menu()

    open_xml = file_menu.Append(wx.ID_ANY, self.menu.menus['importXml'][self.lang], 'open a xml file with tool data')
    self.Bind(event=wx.EVT_MENU, handler=self.on_open_xml,source=open_xml,)

    importStep = file_menu.Append(wx.ID_ANY, self.menu.menus['importSTEP'][self.lang], 'import tool data from a step file')
    self.Bind(event=wx.EVT_MENU, handler=self.on_import_step,source=importStep)
    
    #self.Bind(event=wx.EVT_ENTER_WINDOW, handler=self.help,source=importStep)
    
    ISO13999 = file_menu.Append(wx.ID_ANY, self.menu.menus['pasteISO'][self.lang], 'paste tool data ISO13999')        
    self.Bind(event=wx.EVT_MENU, handler=self.on_paste_iso13999,source=ISO13999,)

    #exp_xml = file_menu.Append(wx.ID_ANY, self.menu.get_menu("exportXml"), 'export tool data into XML file')
    #self.Bind(event=wx.EVT_MENU, handler=self.on_export_xml,source=exp_xml)

    find_tool = file_menu.Append(wx.ID_ANY, self.menu.menus['findTool'][self.lang], 'find tool data')
    self.Bind(event=wx.EVT_MENU, handler=self.on_find_tool,source=find_tool)
    
    exit = file_menu.Append(wx.ID_ANY, self.menu.get_menu('exit'), "close app")

    self.Bind(event=wx.EVT_MENU,handler=self.close_app,source=exit)

    # add file menu to menu bar
    menu_bar = wx.MenuBar()
    menu_bar.Append(file_menu, self.menu.get_menu("file"))

    # add tools config menu
    config = wx.Menu()
    toolSetup = config.Append(wx.ID_ANY, self.menu.get_menu("tool_setup"), 'setup tool data')
    self.Bind( event=wx.EVT_MENU, handler=self. toolSetupPanel, source=toolSetup)
    # add holders config menu
    holdersConfig = config.Append(wx.ID_ANY, self.menu.get_menu("holder_setup"), 'setup holder data')        
    self.Bind(event=wx.EVT_MENU,handler=self.HoldersSetupPanel,source=holdersConfig)
    # add language submenu
    self.language_menu = wx.Menu()
       
    self.language_menu.Append(0, 'English', 'English')
    self.language_menu.Append(1, 'Français', 'Français')
    self.language_menu.Append(2, 'Português', 'Português')

    self.language_menu.Bind(event=wx.EVT_MENU,handler=self.change_language)

    config.AppendSubMenu(self.language_menu, self.menu.get_menu("language"))

    menu_bar.Append(config, f'&{self.menu.get_menu("setup")}')

    # add help menu
    help_menu = wx.Menu()
    help = help_menu.Append(wx.ID_ANY, f"&{self.menu.get_menu('help')}\tF1", 'help')
    self.Bind(event=wx.EVT_MENU,handler=self.help,source=help)
    about = help_menu.Append(wx.ID_ANY, f"{self.menu.get_menu('about')}\t&A", 'about')
    self.Bind(event=wx.EVT_MENU,handler=self.about,source=about)
    menu_bar.Append(help_menu, self.menu.get_menu("help"))

    self.SetMenuBar(menu_bar)
    
    