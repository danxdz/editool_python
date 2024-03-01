import wx
import os
import sys
import logging


from gui.menus_inter import MenusInter

from gui.toolList import ToolList
from gui.toolSetup import toolSetupPanel

from gui.guiTools import refreshToolList
from gui.guiTools import tooltypesButtons
from gui.guiTools import build_menus
from gui.guiTools import load_masks
from gui.guiTools import get_custom_settings

from databaseTools import load_tools_from_database

from importHolders.holdersPanel import HoldersSetupPanel

from importTools.validateImportDialogue import validateToolDialog

from importTools import import_past
from importTools import import_xml_wx

from export_xml_wx import create_xml_data

from tool import ToolsCustomData

from topsolid_api import TopSolidAPI

#from share.save_supabase import read_menu


class ToolManagerUI(wx.Frame):
    BACKGROUND_COLOUR = wx.Colour(240, 240, 240)
    TOOL_TYPE_ALL = "all"
    PANEL_POSITION = (0, 0)

    def __init__(self, parent, id, title):
        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent, title=title, style=no_resize)

        self.ts = TopSolidAPI()
        
        self.selected_tooltype_name = "all"
        self.selected_toolType = -1
        self.icons_bar_widget = None

        self.setupUI()

        #add F1 key to the help menu
        f1_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.help, id=f1_id)
        self.Bind(wx.EVT_ENTER_WINDOW, self.help, id=f1_id)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_F1, f1_id )])
        self.SetAcceleratorTable(accel_tbl)

    def setupUI(self):
        '''Setup the gUI'''
                
        logging.info('loading gUI')

        self.SetBackgroundColour(self.BACKGROUND_COLOUR)

        # load the default tool data
        #menu = read_menu()
        #print("menu :: ", menu)
        #TODO backup menu to text file

        self.menu = {}
        get_custom_settings(self)

        build_menus(self)

        self.menu = MenusInter(self.lang)

        self.toolData = self.loadToolData()
     
        self.main_sizer = self.createMainSizer()
        self.statusBar = self.createStatusBar()
        self.setFrameSizeAndPosition()

    
    def loadToolData(self):
        toolData = ToolsCustomData()
        toolData.get_custom_ts_models()
        
        toolData.full_tools_list, existent_tooltypes = load_tools_from_database(-1, self.lang)
        
        for existent_tooltype in existent_tooltypes:
            toolData.existent_tooltypes.append(int(existent_tooltype))
        toolData.tool_names_mask = load_masks()
        
        print("INFO :: toolData.existent_tooltypes :: ", toolData.existent_tooltypes , " len :: " , len(toolData.existent_tooltypes))
        toolData.selected_tool = -1
        if len(toolData.full_tools_list)>0:
            toolData.selected_tool = toolData.full_tools_list[0]
  
        return toolData

    def createMainSizer(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.icons_bar_widget = tooltypesButtons(self)
        #print("self.icons_bar_widget :: ", self.icons_bar_widget)
        main_sizer.Add(self.icons_bar_widget,  0, wx.ALL | wx.CENTER, 5)

        self.panel = ToolList(self)

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
        self.toolData.full_tools_list, existent_tooltypes = load_tools_from_database(self.selected_toolType, self.lang)
        for existent_tooltype in existent_tooltypes:
                if int(existent_tooltype) not in self.toolData.existent_tooltypes:
                    self.toolData.existent_tooltypes.append(int(existent_tooltype))
    
        refreshToolList(self.panel, self.toolData)

        # Remove the old icons bar from the main sizer
        self.main_sizer.Hide(self.icons_bar_widget)
        self.main_sizer.Remove(self.icons_bar_widget)

        # Create a new icons bar and add it to the main sizer
        self.icons_bar_widget = tooltypesButtons(self)
        #print("self.icons_bar_widget :: ", self.icons_bar_widget)
        self.main_sizer.Insert(0,self.icons_bar_widget, 0, wx.ALL | wx.CENTER, 5)
        self.main_sizer.Layout()
        self.Refresh()



    #menu bar functions
    def on_open_xml(self, event):
        '''open a xml file and convert it to a tool'''
        logging.info('import from xml file')
        #print(": import from xml file :: menu_bar")
        title = f"{self.menu.get_menu('importXml').capitalize()}"
        wcard ="XML files (*.xml)|*.xml"
        tools = import_xml_wx.open_file(self, title, wcard)
        #print("tools :: ", tools, len(tools))


        for tool in tools:
            validateToolDialog(self.panel, tool, True).ShowModal()

        if len(tools) > 0:
            #self.toolData.full_tools_list = refreshToolList(self.panel, tools[len(tools)-1].toolType)
            self.statusBar.SetStatusText(self.getLoadedTools())
            refreshToolList(self.panel, self.toolData)
            
        else:
            print("no tools loaded")
            self.statusBar.SetStatusText("no tools loaded")
            
    
    def on_import_step(self, event):
        '''import a step file and convert it to a tool'''

        title = "Import Step file"
        wcard ="Step files (*.stp)|*.stp"
        if not self.ts or not self.ts.connected:
            self.ts = TopSolidAPI()
        
        dlg = wx.FileDialog(self, "Choose a STEP file to import", wildcard=wcard, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            file_path = dlg.GetPath()
            dlg.Destroy()

            owner_id = 1

            document_name = os.path.basename(file_path)

            lib, name = self.ts.get_current_project()

        try:
            imported_documents, log, bad_document_ids = self.ts.Import_file_w_conv(10, file_path, lib)
            
            if imported_documents:
                print(f"Documents imported successfully. Document IDs: {len(imported_documents)}", "Success", wx.OK | wx.ICON_INFORMATION)
                for doc in imported_documents:
                    print(len(doc), doc)
                    for d in doc:
                        print(d)
                        self.ts.check_in(d)
            else:
                wx.MessageBox(f"Error importing documents. Log: {log}. Bad Document IDs: {bad_document_ids}", "Error", wx.OK | wx.ICON_ERROR)

        except Exception as e:
            wx.MessageBox(f"Error importing documents: {e}", "Error", wx.OK | wx.ICON_ERROR)



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

 

    def change_language(self, event):
        '''change the language of the UI'''
        #get the language index
        lang_index = event.GetId()

        lang = self.menu.get_language_by_id(lang_index)

        #set the language
        self.menu.set_lang(lang)        

        #reload the text from the language file and refresh the UI
        print("reloading gUI", lang)
        logging.info(f"reloading gUI :: {lang}")
        build_menus(self)
        #refresh the panel
        

        

    def help(self, event):
        print(f"help :: {event.GetId()}")
        logging.info(f"{self.statusBar.GetStatusText()}")
    
    def about(self, event):
        wx.MessageBox("ediTool - tools manager\n\nVersion 0.1\n2024", "About ediTool", wx.OK | wx.ICON_INFORMATION)
        
    def exit(self, event):
        print("exit")
        self.Close()
