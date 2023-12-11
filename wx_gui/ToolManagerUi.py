import wx
import sys

import import_xml_wx as iXml

from export_xml_wx import create_xml_data
from gui.toolPanel import ToolPanel
from importTools.pasteDialog import pasteDialog

import ts

class ToolManagerUI(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Tool Manager')
        self.panel = ToolPanel(self, self)
        self.create_menu()
        self.SetSize(800, 800)
        self.Centre()
        self.Show()
        self.tools_list = []

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
        menu_bar.Append(file_menu, '&File')
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_xml,
            source=open_xml,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.paste_iso13999,
            source=ISO13999,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_zip,
            source=open_zip,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.export_xml,
            source=exp_xml,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.close_app,
            source=exit
        )
        self.SetMenuBar(menu_bar)

        #add icon to toolbar with tooltip

        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((15,28))
        self.toolbar.AddTool(1, "endMill", wx.Bitmap("icons/fr2t.png"))
        self.toolbar.AddTool(2, "radiusMill", wx.Bitmap("icons/frto.png"))
        self.toolbar.AddTool(3, "ballMill", wx.Bitmap("icons/frhe.png"))

        self.toolbar.Realize()
        
        self.toolbar.Bind(wx.EVT_TOOL, self.toolTypeSel, id=1)
        self.toolbar.Bind(wx.EVT_TOOL, self.toolTypeSel, id=2)
        self.toolbar.Bind(wx.EVT_TOOL, self.toolTypeSel, id=3)
    
    
    #TODO: add tool type selection
    def toolTypeSel(self, id):
        print("id: ", id)

        
    def on_open_xml(self, event):
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tool = iXml.open_file(self, title, wcard)
        print("tool : ", tool)
        if tool:
            print("Tool added:", tool.Name)
            index = self.panel.add_line(tool)
            #self.tools_list.append(tool)
            self.panel.list_ctrl.Select(index)

    def paste_iso13999(self, event):
        title = "Paste ISO13999 data"        
        pasteDialog(title).ShowModal()

    def on_open_zip(self, event):
        title = "Choose a Zip file:"
        wcard ="Zip files (*.zip)|*.zip"
        iXml.open_file(self, title, wcard)    
    
    def export_xml(self, event):
        print("export_xml")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tool = self.panel.get_selected_item()
        print("tool :: ", tool)
        xml_data = create_xml_data(tool)
        #iXml.save_file(self, title, wcard, xml_data)

    def close_app(event, handle):
        print("exit",event.Title, handle, sep=" :: ")
        sys.exit()        
    
