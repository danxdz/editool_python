import wx
import ts as ts

class EditDialog(wx.Dialog):
    def __init__(self, tool):
        title = f'Editing "{tool.Name}"'
        super().__init__(parent=None, title=title)
        self.tool = tool
        self.main_sizer = wx.GridSizer(rows = 0, cols = 3, hgap = 5, vgap = 5)
                
        #Attributes from Tool class
        #get all Tool attributes
        self.toolAttributes = self.tool.getAttributes()
        
        for key, value in self.toolAttributes.items():
            print(key, value)
            self.add_widgets(key, wx.TextCtrl(self, value=str(value)))

        #TODO: add a combobox for toolType
        #TODO: add a combobox for GroupeMat
        #TODO: add a combobox for ArrCentre
        #TODO range items in grid

        # Add save and cancel buttons        
        btn_sizer = wx.BoxSizer()
        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 5, wx.ALL, 15)

        btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 5, wx.ALL, 15)  

        
        create_btn = wx.Button(self, label='Create')
        create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        btn_sizer.Add(create_btn, 5, wx.ALL, 15)

        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(self.main_sizer)

        #resize the dialog to fit the content
        self.Fit()


    def add_widgets(self, label, widget):
        #HOW TO ADD THE LABEL OVER THE TXTCTRL?

        label_text = wx.StaticText(self, label=label)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label_text, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(widget, 0, wx.ALL, 2)
        self.main_sizer.Add(sizer, 0, wx.ALL, 5)


    def on_save(self, event):
        # Update the Tool object with the edited values
        self.tool.Name = self.main_sizer.GetItemCount()
        print(self.tool.Name)

        # Add your save logic here
        # For example, you might want to update the database with the changes
        # db.update_tool(self.tool)
        self.Destroy()  # Close the dialog after saving

    def on_create(self, event):
        self.tool.Name = self.main_sizer.GetItemCount()
        
        ts.copy_tool(self.tool)
        print("tool :: ", self.tool)
    