import wx
import sys


from gui.toolList import ToolList
from gui.toolSetup import toolSetupPanel
from gui.guiTools import refreshToolList
from gui.guiTools import tooltypesButtons
from gui.guiTools import create_menu
from gui.guiTools import load_masks

from databaseTools import load_tools_from_database

from importHolders.holdersPanel import HoldersSetupPanel

from importTools.validateImportDialogue import validateToolDialog

from importTools import import_past
from importTools import import_xml_wx

from export_xml_wx import create_xml_data

from tool import ToolsCustomData


class ToolManagerUI(wx.Frame):
    BACKGROUND_COLOUR = wx.Colour(240, 240, 240)
    TOOL_TYPE_ALL = "all"
    PANEL_POSITION = (0, 0)

    def __init__(self, parent, id, title):
        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent, title=title, style=no_resize)
        self.Center()

        self.setupUI()

    def setupUI(self):
        self.SetBackgroundColour(self.BACKGROUND_COLOUR)
        self.toolData = self.loadToolData()
        self.toolDefData = self.loadToolDefData()
        self.selected_tooltype_name = "all"
        self.selected_toolType = -1
        self.icons_bar_widget = None
        create_menu(self)
        self.main_sizer = self.createMainSizer()
        self.statusBar = self.createStatusBar()
        self.setFrameSizeAndPosition()

    def loadToolDefData(self):
        toolDefData = ToolsCustomData()
        if len(self.toolData.full_tools_list)>0:
            toolDefData.selected_tool = self.toolData.full_tools_list[0]
        return toolDefData
    
    def loadToolData(self):
        toolData = ToolsCustomData()
        toolData.get_custom_ts_models()
        toolData.full_tools_list, existent_tooltypes = load_tools_from_database(-1)
        for existent_tooltype in existent_tooltypes:

            toolData.existent_tooltypes.append(int(existent_tooltype))
        toolData.tool_names_mask = load_masks()
        print("toolData.existent_tooltypes :: ", toolData.existent_tooltypes , len(toolData.existent_tooltypes))
  

        return toolData

    def createMainSizer(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.icons_bar_widget = tooltypesButtons(self)
        
        main_sizer.Add(self.icons_bar_widget,  0, wx.ALL | wx.CENTER, 5)

        self.panel = ToolList(self, self.toolData)
        main_sizer.Add(self.panel, 1, wx.ALL | wx.CENTER | wx.EXPAND, 15)
        self.SetSizer(main_sizer)
        return main_sizer

    def createStatusBar(self):
        statusBar = self.CreateStatusBar()
        out = self.getLoadedTools()
        statusBar.SetStatusText(out)
        return statusBar

    def setFrameSizeAndPosition(self):
        screenWidth, screenHeight = wx.GetDisplaySize()
        self.SetSize(int(screenWidth / 3), int(screenHeight) - 100)
        self.SetPosition(self.PANEL_POSITION)
        self.Show()
        


    def getLoadedTools(self):
        out = f"no tools :: type : {self.selected_tooltype_name}"
        if self.toolData.full_tools_list:
            numTools = len(self.toolData.full_tools_list) or 0
            if numTools == 1:
                out = f" {numTools} tool :: type : {self.selected_tooltype_name}"
            if numTools > 1:
                out = f" {numTools} tools :: type : {self.selected_tooltype_name}"
        return out
    
                
    def filterToolType(self, event):
        i = event.GetId()
        print("filterToolType :: ", i)
        if i >= 0:
            #get the tool type name
            self.selected_tooltype_name = self.toolData.tool_types_list[i]
            self.selected_toolType = i
            #print(f":: filterToolType {self.toolType} :: {self.toolTypeName} :: {i}" )   
        else:
            #print("no filter")
            self.selected_toolType = -1
        self.toolData.full_tools_list, existent_tooltypes = load_tools_from_database(self.selected_toolType)
        for existent_tooltype in existent_tooltypes:
                if int(existent_tooltype) not in self.toolData.existent_tooltypes:
                    self.toolData.existent_tooltypes.append(int(existent_tooltype))
    
        refreshToolList(self.panel, self.toolData.full_tools_list, self.selected_toolType)


        # Remove the old icons bar from the main sizer
        self.main_sizer.Hide(self.icons_bar_widget)
        self.main_sizer.Remove(self.icons_bar_widget)

        # Create a new icons bar and add it to the main sizer
        self.icons_bar_widget = tooltypesButtons(self)
        print("self.icons_bar_widget :: ", self.icons_bar_widget)
        self.main_sizer.Insert(0,self.icons_bar_widget, 0, wx.ALL | wx.CENTER, 5)
        self.main_sizer.Layout()
        self.Refresh()










    #menu bar functions
    def on_open_xml(self, event):
        print(": import from xml file :: menu_bar")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tools = import_xml_wx.open_file(self, title, wcard)
        #print("tools :: ", tools, len(tools))


        for tool in tools:
            validateToolDialog(self.panel, tool, True).ShowModal()

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