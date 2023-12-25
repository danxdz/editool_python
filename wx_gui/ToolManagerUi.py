import wx
import sys

from gui.toolList import ToolList
from gui.toolSetup import toolSetupPanel
from gui.guiTools import refreshToolList
from gui.guiTools import getToolTypes


import databaseTools as db

from importTools.pasteDialog import pasteDialog
from importHolders.holdersPanel import HoldersSetupPanel

import import_xml_wx as iXml
from export_xml_wx import create_xml_data


class ToolManagerUI(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title="ediTool - tools manager")

        
        #create dictionary with tool types and icon files
        self.toolTypesList , self.tsModelsList = getToolTypes()
        
        print("toolTypesList :: ", self.toolTypesList)
        print("tsModelsList :: ", self.tsModelsList)

        self.panel = ToolList(self, self.toolTypesList)

        self.create_menu()
        self.SetSize(800, 800)
        self.Centre()
        self.Show()
        

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()

        open_xml = file_menu.Append(
            wx.ID_ANY, 'Open xml file', 
            'open a xml file with tool data'
        )
        ISO13999 = file_menu.Append(
            wx.ID_ANY, 'Paste tool ISO13999', 
            'paste tool data ISO13999'
        )
        open_zip = file_menu.Append(
            wx.ID_ANY, 'Open zip file', 
            'open a zip file with tool data'
        )
        exp_xml = file_menu.Append(
            wx.ID_ANY, 'Export XML file', 
            'export tool data into XML file'
        )
        exit = file_menu.Append(
            wx.ID_ANY, "exit", "close app"
        )
        

        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_xml,
            source=open_xml,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_paste_iso13999,
            source=ISO13999,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_zip,
            source=open_zip,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_export_xml,
            source=exp_xml,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.close_app,
            source=exit
        )

        menu_bar.Append(file_menu, '&File')

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

        #add icon to toolbar with tooltip
        self.toolbar = self.CreateToolBar()

        #TODO read app prefs to get toolbar icon size
        self.toolbar.SetToolBitmapSize((20,40))
      
        #need to add first icon 0 no filter to show all tools its not on the list
        icon = "icons/nofilter.png"
        icon = self.toolbar.AddTool(0, "0" , wx.Bitmap(icon))
        icon.SetShortHelp("no filter")
        self.toolbar.Bind(wx.EVT_TOOL, self.filterToolType)

        #add separator
        self.toolbar.AddSeparator()

        #add tool types icons to toolbar start on 1, icons on list start on 0
        for i, toolType in enumerate(self.toolTypesList):
            icon = "icons/" + toolType + ".png"
            #print("icon :: ", icon)
            icon = self.toolbar.AddTool(i+1, toolType , wx.Bitmap(icon))
            icon.SetShortHelp(toolType)
            self.toolbar.Bind(wx.EVT_TOOL, self.filterToolType)

        #add separator
        self.toolbar.AddSeparator()

         # Combo Box (Dropdown) toolbar
        combo = wx.ComboBox(self.toolbar, choices=["Selection 1", "Selection 2"])
        self.toolbar.AddControl(combo)
        
        self.Centre()
        self.toolbar.Realize()     
            
    def filterToolType(self, event):
        #get the tool type name from the dictionary
        self.toolTypeName = self.toolTypesList[event.GetId()]
        #get the index in the dictionary
        self.toolType = str(event.GetId())

        print(f":: filterToolType {self.toolType} :: {self.toolTypeName}")    
        
        refreshToolList(self.panel, self.toolType)
   
    #menu bar functions
    def on_open_xml(self, event):
        print("import from xml file")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tools = iXml.open_file(self, title, wcard)


        for tool in tools:
            save_tool = db.saveTool(tool, self.toolTypesList)
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