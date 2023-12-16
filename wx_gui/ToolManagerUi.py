import wx
import sys

import import_xml_wx as iXml

from export_xml_wx import create_xml_data
from gui.toolList import ToolList
from gui.guiTools import load_tools

from importTools.pasteDialog import pasteDialog

from gui.toolSetup import toolSetupPanel


class ToolManagerUI(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Tool Manager')
        #load tools from database to ToolPanel
        
        self.toolType = "endMill"        

        self.panel = ToolList(self, self)
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


        self.SetMenuBar(menu_bar)


        #add icon to toolbar with tooltip

        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((15,28))
        self.toolbar.AddTool(1, "endMill", wx.Bitmap("icons/fr2t.png"))
        self.toolbar.AddTool(2, "radiusMill", wx.Bitmap("icons/frto.png"))
        self.toolbar.AddTool(3, "ballMill", wx.Bitmap("icons/frhe.png"))
        self.toolbar.AddTool(4, "drill", wx.Bitmap("icons/drill.png"))

        self.toolbar.Realize()
        
        self.toolbar.Bind(wx.EVT_TOOL, self.toolTypeSel, id=1)
        self.toolbar.Bind(wx.EVT_TOOL, self.toolTypeSel, id=2)
        self.toolbar.Bind(wx.EVT_TOOL, self.toolTypeSel, id=3)
        self.toolbar.Bind(wx.EVT_TOOL, self.toolTypeSel, id=4)



    
    
    #TODO: add tool type selection
    def toolTypeSel(self, event):
        case = {
            1: "endMill",
            2: "radiusMill",
            3: "ballMill",
            4: "drill",
        }
        self.toolType = case.get(event.GetId(), "endMill")
        print("toolType filter: ", self.toolType)
        load_tools(self.panel, self.toolType)
    
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