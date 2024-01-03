import wx
import sys, os
import wxgl


from gui.toolList import ToolList
from gui.toolSetup import toolSetupPanel
from gui.guiTools import refreshToolList
from gui.guiTools import tooltypesButtons
from gui.guiTools import create_menu


from importHolders.holdersPanel import HoldersSetupPanel

from importTools.validateImportDialogue import validateToolDialog

from importTools import import_past
from importTools import import_xml_wx

from export_xml_wx import create_xml_data

from tool import ToolsCustomData


class ToolManagerUI(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, title=title, size=(1200, 800), style=wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE)
        self.Center()

        
        self.SetBackgroundColour(wx.Colour(240, 240, 240)) #set background color  
        
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

        self.scene = wxgl.wxscene.WxScene(self, self.draw())
        self.visible = True

         
        self.toolData.fullToolsList = []
        tools = refreshToolList(self.panel,-1)
        if tools:
            if len(tools) > 0:
                self.toolData.fullToolsList = tools
            

        self.toolTypeName = "all"
        

        self.main_sizer.Add(self.panel, 0, wx.ALL, 15)
        self.panel.Center()


        self.statusBar = self.CreateStatusBar()
       
        out = self.getLoadedTools()

        self.statusBar.SetStatusText(out)
        
        self.main_sizer.Add(self.scene, 1, wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM, 5)


        self.SetSize(800, 800)
        self.Centre()
        self.Show()
        
    def draw(self):

        tf = ((0,0,1, 90),(5,-5,0) )
        sch = wxgl.Scheme(bg=(0,0,0))

        sch._reset()

        light = wxgl.SunLight(direction=(0.5,-0.5,-1), diffuse=0.7, specular=0.98, shiny=100, pellucid=0.9)

        sch.sphere((0,0,0), .5, color="orange", name="cudgel")
        sch.cylinder((0,0,0), (2,0,0), .5, color="orange",  name="cudgel")
        sch.cylinder((2,0,0), (3,0,0), .48, color="gray", name="cudgel")
        sch.cylinder((3,0,0), (5,0,0), .5, color="gray",  name="cudgel")
        
        sch.circle((5,0,0), .5, color="#656176",  name="cudgel", light=light, inside=True,transform=tf)



        #sch.axes()

        return sch
    
    def on_home(self, evt):
        self.scene.home()
    def on_animate(self, evt):
        self.scene.pause()
    def on_visible(self, evt):
        self.visible = not self.visible
        self.scene.set_visible('cudgel',self.visible)
    def on_save(self, evt):
        im = self.scene.get_buffer()

        wildcard = "PNG (*.png)|*.png||JPEG (*.jpg)|*.jpg||BMP (*.bmp)|*.bmp||TIFF (*.tif)|*.tif||GIF (*.gif)|*.gif"
        dlg = wx.FileDialog(self, "Save image as...", wildcard=wildcard, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            fn = dlg.GetPath()
            name, ext = os.path.splitext(fn)

            if ext == '.jpg':
                ext = ['.jpg', '.jpeg'][dlg.GetFilterIndex()]
            else:
                im.save('%s%s' % (name, ext))
        dlg.Destroy()


    def getLoadedTools(self):
        out = f"no tools :: type : {self.toolTypeName}"
        if self.toolData.fullToolsList:
            numTools = len(self.toolData.fullToolsList) or 0
            if numTools == 1:
                out = f" {numTools} tool :: type : {self.toolTypeName}"
            if numTools > 1:
                out = f" {numTools} tools :: type : {self.toolTypeName}"
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
        tools = import_xml_wx.open_file(self, title, wcard)
        print("tools :: ", tools, len(tools))


        for tool in tools:
            validateToolDialog(self.panel, tool).ShowModal()

        if len(tools) > 0:
            self.toolData.fullToolsList = refreshToolList(self.panel, tools[len(tools)-1].toolType)
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