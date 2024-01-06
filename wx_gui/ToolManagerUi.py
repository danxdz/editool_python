import wx
import sys


from gui.toolList import ToolList
from gui.toolSetup import toolSetupPanel
from gui.guiTools import refreshToolList
from gui.guiTools import tooltypesButtons
from gui.guiTools import create_menu

from databaseTools import load_tools_from_database

from importHolders.holdersPanel import HoldersSetupPanel

from importTools.validateImportDialogue import validateToolDialog

from importTools import import_past
from importTools import import_xml_wx

from export_xml_wx import create_xml_data

from tool import ToolsCustomData


class ToolManagerUI(wx.Frame):
    def __init__(self, parent, id, title):
        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent, title=title, style= no_resize)
        self.Center()

        self.SetBackgroundColour(wx.Colour(240, 240, 240)) #set background color  

        #create dictionary with tool types and ts models
        self.toolData = ToolsCustomData()
        self.toolData.get_custom_ts_models()
        print("toolData :: tooltypes : ", self.toolData.tool_types_list)
        print("toolData :: tsModels ", self.toolData.ts_models)
        print("toolData :: toolTypesNumbers ", self.toolData.tool_type_numbers)
        #load all tools from database
        self.toolData.full_tools_list = load_tools_from_database(-1)
        print("toolData :: full_tools_list ", len(self.toolData.full_tools_list))

        #create menu bar
        create_menu(self)

        #create a container to hold the buttons
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
     
        tooltypesButtons(self)
        
        #create the panel with the tool list
        self.panel = ToolList(self, self.toolData)
        
        self.main_sizer.Add(self.panel, 1, wx.ALL | wx.EXPAND, 15)  # Add wx.EXPAND flag


        self.toolTypeName = "all"
        
        

        self.statusBar = self.CreateStatusBar()
       
        out = self.getLoadedTools()

        self.statusBar.SetStatusText(out)
        
        self.SetSizer(self.main_sizer)  # Set the sizer to the frame

        self.SetSize(600, 1000)
        self.Centre()
        self.Show()
        


    def getLoadedTools(self):
        out = f"no tools :: type : {self.toolTypeName}"
        if self.toolData.full_tools_list:
            numTools = len(self.toolData.full_tools_list) or 0
            if numTools == 1:
                out = f" {numTools} tool :: type : {self.toolTypeName}"
            if numTools > 1:
                out = f" {numTools} tools :: type : {self.toolTypeName}"
        return out
    
                
    def filterToolType(self, event):
        i = event.GetId()
        print("filterToolType :: ", i)
        if i >= 0:
            #get the tool type name
            self.toolTypeName = self.toolData.tool_types_list[i]
            self.toolType = i
            #print(f":: filterToolType {self.toolType} :: {self.toolTypeName} :: {i}" )   
        else:
            #print("no filter")
            self.toolType = -1
        self.toolData.full_tools_list = load_tools_from_database(self.toolType)
        refreshToolList(self.panel, self.toolData.full_tools_list, self.toolType)
        
        self.statusBar.SetStatusText(self.getLoadedTools())


    #menu bar functions
    def on_open_xml(self, event):
        print(": import from xml file :: menu_bar")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tools = import_xml_wx.open_file(self, title, wcard)
        #print("tools :: ", tools, len(tools))


        for tool in tools:
            validateToolDialog(self.panel, tool).ShowModal()

        if len(tools) > 0:
            #self.toolData.full_tools_list = refreshToolList(self.panel, tools[len(tools)-1].toolType)
            self.statusBar.SetStatusText(self.getLoadedTools())
        else:
            print("no tools loaded")
            self.statusBar.SetStatusText("no tools loaded")


    def on_paste_iso13999(self, event):
        title = "Paste ISO13999 data" 
        import_past.open_file(self, title)         

        #pasteDialog(self.panel, title).ShowModal()

    def on_open_zip(self, event):
        title = "Choose a Zip file:"
        wcard ="Zip files (*.zip)|*.zip"
        import_xml_wx.open_file(self, title, wcard)   #TODO: add zip file import  - get p21 data from zip file 
    
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