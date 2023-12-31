import wx
import sys


from gui.toolList import ToolList
from gui.toolSetup import toolSetupPanel
from gui.guiTools import refreshToolList
from gui.guiTools import tooltypesButtons
from gui.guiTools import create_menu

from importTools.pasteDialog import pasteDialog
from importHolders.holdersPanel import HoldersSetupPanel

from importTools.validateImportDialogue import validateToolDialog

import importTools.import_xml_wx as iXml

from export_xml_wx import create_xml_data

from tool import ToolsCustomData


class ToolManagerUI(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, title=title)
        
        self.SetBackgroundColour(wx.Colour(240, 240, 250))  # Change this to the color you want     
        
        #create dictionary with tool types and ts models
        self.toolData = ToolsCustomData()
        self.toolData = self.toolData.getCustomTsModels()
        print("toolData :: tooltypes : ", self.toolData.toolTypesList)
        print("toolData :: tsModels ", self.toolData.tsModels)
        print("toolData :: toolTypesNumbers ", self.toolData.toolTypesNumbers)

        create_menu(self)

        #create a container to hold the buttons
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
     
        tooltypesButtons(self)
        
        #create the panel with the tool list
        self.panel = ToolList(self, self.toolData)
        #load tools from database to list control   
         
        self.toolData.fullToolsList = refreshToolList(self.panel,-1) or []
        self.toolTypeName = "all"
        

        self.main_sizer.Add(self.panel, 0, wx.ALL, 15)
        self.panel.Center()


        self.statusBar = self.CreateStatusBar()
       
        out = self.getLoadedTools()

        self.statusBar.SetStatusText(out)

        self.SetSize(800, 800)
        self.Centre()
        self.Show()
        


    def getLoadedTools(self):
        out = f"no tools loaded type : {self.toolTypeName}"
        if self.toolData.fullToolsList:
            numTools = len(self.toolData.fullToolsList) or 0
            if numTools > 0:
                out = f":: {numTools} tools loaded :: type : {self.toolTypeName}"
                
        return out
                
    def filterToolType(self, event):
        i = event.GetId()
        #print("filterToolType :: ", i)
        if i >= 0:
            #get the tool type name
            self.toolTypeName = self.toolData.toolTypesList[i]
            self.toolType = i
            #print(f":: filterToolType {self.toolType} :: {self.toolTypeName} :: {i}" )   
        else:
            #print("no filter")
            self.toolType = -1
        
        self.toolData.fullToolsList = refreshToolList(self.panel, self.toolType)
        
        self.statusBar.SetStatusText(self.getLoadedTools())



    #menu bar functions
    def on_open_xml(self, event):
        print("import from xml file")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tools = iXml.open_file(self, title, wcard)
        print("tools :: ", tools, len(tools))


        for tool in tools:
            valid = validateToolDialog(self.panel, tool).ShowModal()
            print("tool :::::::::::: ", valid)
            #db.saveTool(tool, self.toolData.toolTypes)
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