import wx
import sys, os

import import_xml_wx as iXml

import databaseTools as db

from export_xml_wx import create_xml_data
from gui.toolList import ToolList
from databaseTools import getToolTypes

from importTools.pasteDialog import pasteDialog

from gui.toolSetup import toolSetupPanel
from importHolders.holdersPanel import HoldersSetupPanel


class ToolManagerUI(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Tool Manager')
        #load tools from database to ToolPanel
        
        self.toolType = 0

        #create dictionary with tool types and icon files
        self.toolTypes = getToolTypes()

        self.toolTypeName = self.toolTypes[self.toolType]

        self.panel = ToolList(self, self)

        #load tools from database to list control
        print("loading tools :: type : ", self.toolType, " :: ",  self.toolTypeName)
        tools = db.load_tools_from_database(self,self.toolType)
        print("tools loaded :: ", tools)

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
        self.toolbar.SetToolBitmapSize((20,40))
        i = 0
        print("adding icons to toolbar")
        print(self.toolTypes)
        for toolType in self.toolTypes:            
            i += 1
            name = toolType
            #print(name)
            icon = "icons/"+str(i)+"-"+name+".png"
            #print(icon)
            icon = self.toolbar.AddTool(i, str(i) , wx.Bitmap(icon))
            icon.SetShortHelp(name)
            self.toolbar.Bind(wx.EVT_TOOL, self.toolTypeSel)

         # Combo Box (Dropdown) toolbar
        combo = wx.ComboBox(self.toolbar, choices=["Selection 1", "Selection 2"])
        self.toolbar.AddControl(combo)
        
        self.Centre()
        self.toolbar.Realize()     
            
    def toolTypeSel(self, event):        
        self.toolTypeName = self.toolTypes[event.GetId()-1]
        #get the index in the dictionary
        self.toolType = str(event.GetId())

        print("toolType filter: ", self.toolType, self.toolTypeName)
        
        tools = db.load_tools_from_database(self,self.toolType)
        print("tools loaded :: ", tools)
   
    #menu bar functions
    def on_open_xml(self, event):
        print("import from xml file")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tool = iXml.open_file(self, title, wcard)
               

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