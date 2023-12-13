import wx
import ts as ts
import databaseTools

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
            #print(key, value)
            self.add_widgets(key, wx.TextCtrl(self, value=str(value)))

        #TODO: add a combobox for toolType
        #TODO: add a combobox for GroupeMat
        #TODO: add a combobox for ArrCentre
        #TODO range items in grid

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


    def add_widgets(self, label, widget):
        
        label_text = wx.StaticText(self, label=label)
        sizer = wx.BoxSizer(wx.VERTICAL)
        #add binding to widget and send label_text to on_change
        widget.Bind(wx.EVT_TEXT, lambda event: self.on_change(event, label))

        sizer.Add(label_text, 0, wx.ALL, 5)
        sizer.Add(widget, 0, wx.ALL, 5)
        self.main_sizer.Add(sizer, 0, wx.ALL, 5)
                

    def on_save(self, event):
        print("updating tool ", self.tool.Name, " in database")
        #Update the database with the changes
        databaseTools.update_tool(self.tool)        

        #self.Destroy()  # Close the dialog after saving

    def on_create(self, event):

        ts.copy_tool(self.tool)
        #print("tool :: ", self.tool)
        self.Destroy()  # Close the dialog after create tool

    def on_change(self, event, label_text ):
        #get the value of the widget and the textbox name changed
        #print("change",label_text, event.GetString())

        #nice we are getting the value of the widget label, now i need to set the tool attribute
        tool = self.tool
        #set object attribute with the value of the widget
        setattr(tool, label_text, event.GetString())
        self.tool = tool

        #print("gret" , getattr(tool, label_text))    