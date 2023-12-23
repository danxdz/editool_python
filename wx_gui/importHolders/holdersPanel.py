import wx
from ts import copyHolder 
from ts import initFolders


custom_tools_project_name = "Tool Lib"


class HoldersSetupPanel(wx.Dialog):
    def __init__(self, parent):
        title = 'Holders setup'
        super().__init__(parent=None, title=title)

        self.main_sizer = wx.GridSizer(rows = 0, cols = 3, hgap = 5, vgap = 5)
        self.parent = parent
         
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

        self.get_folders()

    def get_folders(self):
        print("get folders")
        initFolders()

    def on_save(self, event):
        print("updating tool ", self.tool.Name, " in database")
        #self.Destroy()  # Close the dialog after saving




    def on_create(self, event):

        copyHolder()
