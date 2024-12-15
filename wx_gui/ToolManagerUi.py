import wx
import sys
import logging
import asyncio
import os

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


from databaseTools import saveTool

from export_xml_wx import create_xml_data

from tool import ToolsCustomData

from topsolid_api import TopSolidAPI

#from share.save_supabase import read_menu

from importTools.dragdrop import FileDrop


from gui.viewer3d.glObjects import glObjects

from help.help import HelpFrame

import locateTools.findTools 

class ToolManagerUI(wx.Frame):
    BACKGROUND_COLOUR = wx.Colour(240, 240, 240)
    TOOL_TYPE_ALL = "all"
    PANEL_POSITION = (0, 0)

    def __init__(self, parent, title):
        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent, title=title, style=no_resize)

        super(ToolManagerUI, self).__init__(parent, title=title)

        self.parent = parent

        self.gl = glObjects(None)

        self.ts = TopSolidAPI()
        self.selected_tooltype_name = "all"
        self.selected_toolType = -1
        self.selected_tool = None
        self.icons_bar_widget = None

        self.mouse_pos = None
        self.lang = -1

        #get the language if it is set or get -1
        self.lang = MenusInter.GetCustomLanguage()
        
        #if the language is not set, get the language of the system
        if self.lang == -1:
            ts_lang = self.ts.get_ts_language()
            MenusInter.set_lang(self, ts_lang)

        self.setupUI()
    
        self.file_drop_target = FileDrop(self,self.gl)
        # Set the drop target for the frame
        self.SetDropTarget(self.file_drop_target)

        #add F1 key to the help menu
        f1_id = wx.NewId()
  
        self.Bind(wx.EVT_MENU, self.help, id=f1_id)
        self.Bind(wx.EVT_ENTER_WINDOW, self.help, id=f1_id)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_F1, f1_id )])
        self.SetAcceleratorTable(accel_tbl)


    def on_quit(self, event):
        '''close the app'''
        self.ts.end_modif()
        self.ts.disconnect_topsolid()
        self.canvas.stop_timer()
        self.Close(True)

    def on_show(self, event):
        self.canvas.show()
        event.Skip()



    def setupUI(self):
        '''load the gUI'''

        self.SetBackgroundColour(self.BACKGROUND_COLOUR)

        build_menus(self)

        self.menu = {}

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
        toolData.selected_tool = None
        if len(toolData.full_tools_list)>0:
            toolData.selected_tool = toolData.full_tools_list[0]
  
        return toolData

    def createMainSizer(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tool_icons = tooltypesButtons(self)
        self.icons_bar_widget = wx.BoxSizer(wx.HORIZONTAL)
        for each in self.tool_icons:
            self.Bind(wx.EVT_BUTTON, self.filterToolType, each)
            self.icons_bar_widget.Add(each, 0, wx.ALL | wx.CENTER, 5)

        #print("self.icons_bar_widget :: ", self.icons_bar_widget)
        main_sizer.Add(self.icons_bar_widget,  0, wx.ALL | wx.CENTER, 5)
        
        '''#create big icon button "plus" to add new tool
        self.plus_icon = wx.BitmapButton(self, -1, wx.Bitmap("icons/plus.png", wx.BITMAP_TYPE_PNG), size=(50, 50))
        self.plus_icon.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.Bind(wx.EVT_BUTTON, self.add_to_assembly, self.plus_icon)
        #create sizer for the plus icon
        self.assemby_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.assemby_sizer.Add(self.plus_icon, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(self.assemby_sizer, 0, wx.ALL | wx.CENTER, 5)'''

        self.panel = ToolList(self, self.gl)

        main_sizer.Add(self.panel, 1, wx.ALL | wx.CENTER | wx.EXPAND, 15)

        self.SetSizer(main_sizer)
        return main_sizer
    
    def add_to_assembly(self, event):
        #add new icon next left to plus icon
        self.plus_icon = wx.BitmapButton(self, -1, wx.Bitmap("icons/plus.png", wx.BITMAP_TYPE_PNG), size=(50, 50))
        self.plus_icon.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.Bind(wx.EVT_BUTTON, self.add_to_assembly, self.plus_icon)
        self.assemby_sizer.Add(self.plus_icon, 0, wx.ALL | wx.CENTER, 5)
        self.main_sizer.Layout()
        self.Refresh()
        self.createNewTool(event)

    def createNewTool(self, event):
        tool_list = self.toolData.full_tools_list
        dialog = wx.Dialog(self, title="Select a Tool", size=(300, 200))
        sizer = wx.BoxSizer(wx.VERTICAL)
        tool_names = [tool.Name for tool in tool_list]
        tool_names.insert(0, "New Tool")
        tool_names.insert(1, "New Tool from File")
        tool_names.insert(2, "New Tool from Clipboard")
        tool_names.insert(3, "New Tool from ISO13999")
        tool_names.insert(4, "New Tool from XML")
        tool_names.insert(5, "New Tool from STEP")

        tool_choice = wx.Choice(dialog, choices=tool_names)
        tool_choice.SetSelection(0)
        sizer.Add(tool_choice, 0, wx.ALL | wx.CENTER, 5)

        ok_button = wx.Button(dialog, wx.ID_OK, "OK")
        ok_button.Bind(wx.EVT_BUTTON, lambda event: self.on_new_tool(event, tool_choice, dialog))
        sizer.Add(ok_button, 0, wx.ALL | wx.CENTER, 5)



    def createStatusBar(self):
        statusBar = self.CreateStatusBar(3)
        out = self.getLoadedTools()
        statusBar.SetStatusText(out)
        #add text to the status bar right side
        text = "topsolid connected" if self.ts.connected else "topsolid not connected"
        statusBar.SetStatusText(text, 2)
        return statusBar

    def setFrameSizeAndPosition(self):
        screenWidth, screenHeight = wx.GetDisplaySize()
        self.SetSize(int(screenWidth / 3)+50, int(screenHeight) - 100)
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
        if i == 99 :
            i = -1
                   
        self.tool_icons[i].SetWindowStyleFlag(wx.BORDER_RAISED)
        self.tool_icons[i].SetBackgroundColour(wx.Colour(240, 240, 240))

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
        #self.main_sizer.Hide(self.icons_bar_widget)
        #self.main_sizer.Remove(self.icons_bar_widget)

        # Create a new icons bar and add it to the main sizer
        #self.icons_bar_widget = tooltypesButtons(self)
        #print("self.icons_bar_widget :: ", self.icons_bar_widget)
        #self.main_sizer.Insert(0,self.icons_bar_widget, 0, wx.ALL | wx.CENTER, 5)
        #self.main_sizer.Layout()
        #self.Refresh()


    def _on_new_tool(self, tools):

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

        self._on_new_tool(tools)            
    
    def on_import_step(self, event, file_path=None):
        '''import a step file and convert it to a tool'''
        
        if not file_path:
            title = "Choose a STEP file to import"
            wcard = "Step files (*.stp, *.step)|*.stp;*.step"
            file_path = FileDialogHandler.open_file_dialog(self, title, wcard)
        
        try:

            FileDrop.OnDropFiles(self.file_drop_target, 0, 0, file_path)
            if not self.ts or not self.ts.connected:
                self.ts = TopSolidAPI()
        
            self.ts.get_current_project()
            msg = f"Error importing documents: "

            #try to end the modification
            try:
                self.ts.end_modif("Importing STEP file",True)
            except Exception as e:
                logging.error(f"No ending modification, can edit: {e}")

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

    def MultilineTextDialog(self, title, message):
        '''dialog to enter a tool ref to find'''
        logging.info('search tool')
        #create a form to enter the tool ref with a multiline text box
        dialog = wx.Frame(self, title=title, size=(300, 250), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = wx.Panel(dialog)
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(panel, label=message)
        sizer.Add(text, 0, wx.ALL | wx.CENTER, 5)
        text_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(250, 100))
        sizer.Add(text_box, 0, wx.ALL | wx.CENTER, 5)
        
        #add a radio button to autosave the tool
        auto_save = wx.CheckBox(panel, label="Auto save")
        sizer.Add(auto_save, 0, wx.ALL | wx.CENTER, 5)

        ok_button = wx.Button(panel, wx.ID_OK, "OK")
        ok_button.Bind(wx.EVT_BUTTON, lambda event: self.on_search_tool(event, text_box, dialog))
        sizer.Add(ok_button, 0, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(sizer)
        dialog.Show()

    def on_search_tool(self, event, text_box, dialog):
        '''search for a tool in internet'''

        ref = text_box.GetValue()
        #find the tool in the database
        #get localpath
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, "tool_parameters.txt")
        #check if is multiline or single line
        if "\n" in ref:
            ref = ref.split("\n")
        else:
            ref = [ref]
        
        for r in ref:
            tool = asyncio.run(locateTools.findTools.search_tool(r, path,self.toolData))
           
            #validateToolDialog(self.panel, tool, True).ShowModal()
             #check if data is not empty
            if tool and tool.name and tool.name != "Name not found":
                    if tool.D1 and tool.D1 != "0":
                        #add tool to tool to database
                        saveTool(tool)
                        self.toolData.full_tools_list.append(tool)
                        refreshToolList(self.panel, self.toolData)
            else:
                wx.MessageBox(f"Tool not found {r}", "Error", wx.OK | wx.ICON_ERROR)

        dialog.Destroy()
       


    def FindToolDialog(self):
        '''dialog to enter a tool ref to find'''
        logging.info('search tool')
        #create a dialog to enter the tool ref with a multiline text box
        self.MultilineTextDialog("Find a tool", "Enter the tool reference")


            
    def on_find_tool(self, event):
        '''find a tool in the database'''
        logging.info('find a tool')
        #check if connection is available ping google
        #if not available, show a message
        google = "www.google.com"
        response = os.system("ping -n 1 " + google)
        if response != 0:
            wx.MessageBox("No internet connection available", "Error", wx.OK | wx.ICON_ERROR)
            return
        
    
        find_tool_dialog = self.FindToolDialog()

        '''tool = asyncio.run(locateTools.findTools.search_tool(["1K223-1000-300-NH H10F"], "tool_parameters.txt"))
        print(tool.name)
        #add the tool to the database
        validateToolDialog(self.panel, tool, True).ShowModal()
        '''
    def on_paste_iso13999(self, event):
        '''paste ISO13999 data and convert it to a tool'''
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
        lang = event.GetId()

        #lang = self.menu.get_language_by_id(lang_index)

        #set the language
        self.lang = self.menu.set_lang(lang)        

        #reload the text from the language file and refresh the UI
        print("reloading gUI", self.lang)
        logging.info(f"reloading gUI :: {self.lang}")

        build_menus(self)


        #refresh the panel
        self.panel.Destroy()
        self.panel = ToolList(self, self.gl)
        self.main_sizer.Add(self.panel, 1, wx.ALL | wx.CENTER | wx.EXPAND, 15)
        self.main_sizer.Layout()
        self.Refresh()

        
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