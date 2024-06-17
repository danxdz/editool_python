import wx
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
from gui.guiTools import FileDialogHandler

from databaseTools import load_tools_from_database
from databaseTools import update_tool

from importHolders.holdersPanel import HoldersSetupPanel

from importTools.validateImportDialogue import validateToolDialog

from importTools import import_past
from importTools import import_xml_wx

from export_xml_wx import create_xml_data

from tool import ToolsCustomData

from topsolid_api import TopSolidAPI

#from share.save_supabase import read_menu

from importTools.dragdrop import FileDrop


from help.help import HelpFrame

class ToolManagerUI(wx.Frame):
    BACKGROUND_COLOUR = wx.Colour(240, 240, 240)
    TOOL_TYPE_ALL = "all"
    PANEL_POSITION = (0, 0)

    def __init__(self, parent, title):
        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent, title=title, style=no_resize)

        super(ToolManagerUI, self).__init__(parent, title=title)

        self.parent = parent

        self.ts = TopSolidAPI()
        self.selected_tooltype_name = "all"
        self.selected_toolType = -1
        self.selected_tool = None
        self.icons_bar_widget = None

        self.mouse_pos = None

        #get ts language
        self.ts_lang = self.ts.get_language()

        #self.lang = MenusInter.GetCustomLanguage(self.ts_lang)

        self.setupUI()

        #add F1 key to the help menu
        f1_id = wx.NewId()
    
        self.file_drop_target = FileDrop(parent,self)
        
        # Set the drop target for the frame
        self.SetDropTarget(self.file_drop_target)
  
        self.Bind(wx.EVT_MENU, self.help, id=f1_id)
        self.Bind(wx.EVT_ENTER_WINDOW, self.help, id=f1_id)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_F1, f1_id )])
        self.SetAcceleratorTable(accel_tbl)

        '''
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        # capture the mouse without turn icon into a hand
        self.CaptureMouse()
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        #add bind to click on the mouse so we can release it
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_click)

    def on_mouse_click(self, event):
        print(f"mouse click :: {event.GetPosition()}")
        #release the mouse
        if self.HasCapture():
            self.ReleaseMouse()
        else:
            self.CaptureMouse()
        #print(f"mouse click :: {event.GetPosition()}")
        '''

    def on_quit(self, event):
        self.canvas.stop_timer()
        self.Close(True)

    def on_show(self, event):
        self.canvas.show()
        event.Skip()


    def setupUI(self):
        '''load the gUI'''

        self.SetBackgroundColour(self.BACKGROUND_COLOUR)

        # load the default tool data
        
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

        #change all tool.imported to False - 0
        for tool in toolData.full_tools_list:
            if tool.imported:
                tool.imported = 0
                #and save it to the database
                update_tool(tool)
        
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


    def on_new_tool(self, tools):

        if not self.ts or not self.ts.connected:
                    self.ts = TopSolidAPI()

        for tool in tools:
            validateToolDialog(self.panel, tool, True).ShowModal()

        if len(tools) > 0:
            #self.toolData.full_tools_list = refreshToolList(self.panel, tools[len(tools)-1].toolType)
            self.statusBar.SetStatusText(self.getLoadedTools())
            refreshToolList(self.panel, self.toolData)            
        else:
            print("no tools loaded")
            self.statusBar.SetStatusText("no tools loaded")


    #menu bar functions
    def on_open_xml(self, event):
        '''open a xml file and convert it to a tool'''
        logging.info('import from xml file')
        #print(": import from xml file :: menu_bar")        
        tools = import_xml_wx.import_xml_file(self, None)
        #print("tools :: ", tools, len(tools))

        self.on_new_tool(tools)            
    
    def on_import_step(self, event, file_path=None):
        '''import a step file and convert it to a tool'''
        
        if not file_path:
            title = "Choose a STEP file to import"
            wcard = "Step files (*.stp, *.step)|*.stp;*.step"
            file_path = FileDialogHandler.open_file_dialog(self, title, wcard)
        
        else:
            try:
                if not self.ts or not self.ts.connected:
                    self.ts = TopSolidAPI()
            
                self.ts.get_current_project()
                msg = f"Error importing documents: "

                imported_documents, log, bad_document_ids = self.ts.Import_file_w_conv(10, file_path, self.ts.current_project)
                
                if imported_documents:
                    print(f"Documents imported successfully. Document IDs: {len(imported_documents)}", "Success", wx.OK | wx.ICON_INFORMATION)
                    for doc in imported_documents:
                        print(len(doc), doc)
                        for d in doc:
                            print(d)
                            self.ts.check_in(d)
                else:
                    wx.MessageBox(f"{msg} Log: {log}. Bad Document IDs: {bad_document_ids}", "Error", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                wx.MessageBox(f"{msg} {e}", "Error", wx.OK | wx.ICON_ERROR)
                logging.error(msg)


    def on_paste_iso13999(self, event):
        title = "Paste ISO13999 data" 
        import_past.open_file(self, title)         

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
        self.panel.Destroy()
        self.panel = ToolList(self)
        self.main_sizer.Add(self.panel, 1, wx.ALL | wx.CENTER | wx.EXPAND, 15)
        self.main_sizer.Layout()
        self.Refresh()

    def on_mouse_move(self, event):
        print(f"mouse move :: {event.GetPosition()}")
        
    def help(self, event):
        print(f"help :: {event.GetId()}")
        logging.info(f"{self.statusBar.GetStatusText()}")
        #show the help file
        HelpFrame(self, "Help",self.lang).Show()
    
    def about(self, event):
        wx.MessageBox("ediTool - Fast, Precise, Automated Editing \n\nVersion 0.1\n2024", "About ediTool", wx.OK | wx.ICON_INFORMATION)
        
    def exit(self, event):
        print("exit")
        self.Close()

    def import_file(self, event):
        print("import_file")