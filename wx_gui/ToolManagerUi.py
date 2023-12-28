import wx
import sys


from gui.toolList import ToolList
from gui.toolSetup import toolSetupPanel
from gui.guiTools import refreshToolList
from gui.guiTools import getToolTypes


import databaseTools as db

from importTools.pasteDialog import pasteDialog
from importHolders.holdersPanel import HoldersSetupPanel

from importTools.validateImportDialogue import validateToolDialog

import import_xml_wx as iXml
from export_xml_wx import create_xml_data



class ToolManagerUI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="ediTool - tools manager")
        
        #create dictionary with tool types and ts models
        self.toolData = getToolTypes()        

        #create the panel with the tool list
        self.panel = ToolList(self, self.toolData)

        self.create_menu()
        self.SetSize(800, 800)
        self.Centre()
        self.Show()
        

    def create_menu(self):
        menu_bar = wx.MenuBar()

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

        #add icons to toolbar
        self.toolbar = self.CreateToolBar()

        #TODO read app prefs to get toolbar icon size
        #self.toolbar.SetToolBitmapSize((20,40))
      
        #add tool types icons to toolbar 
        icon = "icons/nofilter.png"
        icon = self.toolbar.AddTool(-1, "0" , wx.Bitmap(icon))
        icon.SetShortHelp("no filter")
        self.toolbar.Bind(wx.EVT_TOOL, self.filterToolType)

        #add separator
        self.toolbar.AddSeparator()

        #add tool types icons to toolbar
        for i, toolType in enumerate(self.toolData.toolTypes):
            #print(f"i :: {i} :: toolType :: {toolType}")
            icon = "icons/" + toolType + ".png"
            #print("icon :: ", icon)
            icon = self.toolbar.AddTool(i, toolType , wx.Bitmap(icon))
            icon.SetShortHelp(toolType)
            self.toolbar.Bind(wx.EVT_TOOL, self.filterToolType)

        #add separator
        self.toolbar.AddSeparator()
        
        self.Centre()
        self.toolbar.Realize()     

            
    def filterToolType(self, event):
        i = event.GetId()

        if i >= 0:
            #get the tool type name
            self.toolTypeName = self.toolData.toolTypes[i]
            #get the index
            self.toolType = i
            #print(f":: filterToolType {self.toolType} :: {self.toolTypeName} :: {i}" )   
        else:
            #print("no filter")
            self.toolType = -1
        
        refreshToolList(self.panel, self.toolType)



    #menu bar functions
    def on_open_xml(self, event):
        print("import from xml file")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tools = iXml.open_file(self, title, wcard)

        saveTools = validateToolDialog(self.panel, tools).ShowModal()

        for tool in saveTools:
            db.saveTool(tool, self.toolData.toolTypes)
            print("tool added: ", tool.Name)
            refreshToolList(self.panel, tool.toolType)

    def on_paste_iso13999(self, event):
        title = "Paste ISO13999 data"        
        pasteDialog(self.panel, title).ShowModal()

    def on_open_zip(self, event):
        title = "Choose a Zip file:"
        wcard ="Zip files (*.zip)|*.zip"
        iXml.open_file(self, title, wcard)   #TODO: add zip file import  - get p21 data from zip file 
    
    def on_export_xml(self, event):
        print("export_xml")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tool = ToolList.getSelectedTool(self.panel)
        print("tool selected to export :: ", tool.Name)
        xml_data = create_xml_data(tool)

    def close_app(event, handle):
        print("exit",event.Title, handle, sep=" :: ")
        sys.exit()        
    

    def toolSetupPanel(self, event):
        toolSetupPanel(self).ShowModal()

    
    def HoldersSetupPanel(self, event):
        HoldersSetupPanel(self).ShowModal()