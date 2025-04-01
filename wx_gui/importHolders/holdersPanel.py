import wx
import topsolid_api   


custom_tools_project_name = "Tool Lib"


class HoldersSetupPanel(wx.Dialog):
    def __init__(self, parent):
        title = 'Holders setup'
        super().__init__(parent=None, title=title)

        self.parent = parent

        #add panel
        self.panel = wx.Panel(self)
        self.ts = topsolid_api.TopSolidAPI()

        #add sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        #add components
        #combo box for tool type
        self.elemTool = wx.ComboBox(self, style=wx.CB_READONLY)
        self.elemTool.Bind(wx.EVT_COMBOBOX, self.on_tool_type)
        
        elements = self.ts.init_folders()
        print("elements :: ", elements)

        #self.elemTool.SetItems(elements)
        #self.elemTool.SetSelection(0)

        self.main_sizer.Add(self.elemTool, 0, wx.ALL, 5)

        
        # Add save and cancel buttons        
        btn_sizer = wx.BoxSizer()
        save_btn = wx.Button(self, label='save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 5, wx.ALL, 15)

        btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL, label="close"), 5, wx.ALL, 15)  
        
        create_btn = wx.Button(self, label='create')
        create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        btn_sizer.Add(create_btn, 5, wx.ALL, 15)

        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)

        self.SetSizer(self.main_sizer)

        #resize the dialog to fit the content
        self.Fit()

       
    def on_tool_type(self, event):
        print("on tool type")
        

    def get_folders(self):
        print("get folders")
        #title = initFolders()
        #print("title :: " , title)

    def on_save(self, event):
        print("updating tool ", self.tool.Name, " in database")
        #self.Destroy()  # Close the dialog after saving




    def on_create(self, event):
        print("on create")
        #self.Destroy()  # Close the dial


        