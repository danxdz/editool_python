import wx
import ts as ts
import importTools.import_past as import_past
import tool
from databaseTools import saveTool
from databaseTools import load_tools_from_database



class pasteDialog(wx.Dialog):
    def __init__(self,parent, title):
        title = 'Add new tool from ISO13999 data'
        super().__init__(parent=None, title=title)
      
        self.parent = parent

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
                
        self.text_area = wx.TextCtrl(self,style = wx.TE_MULTILINE)
        self.main_sizer.Add(self.text_area, 0, wx.Center)
        
        self.textboxSizer = wx.GridSizer(rows = 0, cols = 3, hgap = 5, vgap = 5)
        self.main_sizer.Add(self.textboxSizer, 0, wx.Center)
                    
        # Add buttons box       
        btn_sizer = wx.BoxSizer()

        refresh_btn = wx.Button(self, label='Refresh')
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        btn_sizer.Add(refresh_btn, 5, wx.ALL, 15)
        
        self.save_btn = wx.Button(self, label='Save')
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(self.save_btn, 5, wx.ALL, 15)
        self.save_btn.Disable()

        create_btn = wx.Button(self, label='Create')
        create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        btn_sizer.Add(create_btn, 5, wx.ALL, 15)
        create_btn.Disable()

        btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 5, wx.ALL, 15)

        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(self.main_sizer)

        #resize the dialog to fit the content
        self.Fit()

    def add_widgets(self, label, widget):
        
        label_text = wx.StaticText(self, label=label)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label_text, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(widget, 0, wx.ALL, 2)
        self.textboxSizer.Add(sizer, 0, wx.ALL, 5)

    def on_refresh(self, event):
        
        #print(str(self.text_area.GetValue()))

        self.tool = import_past.process_input_13999(self.text_area.GetValue())
        #print("tool :: ", self.tool)
        #Attributes from Tool class
        #get all Tool attributes
        self.toolAttributes = self.tool.getAttributes()        

        #clear all widgets
        self.textboxSizer.Clear(True)
        self.main_sizer.Layout()
        self.main_sizer.Fit(self)

        for key, value in self.toolAttributes.items():
            print(key, value)
            #TODO: add combobox for toolType, Manuf, GroupeMat...
            if key == 'toolType':
                self.add_widgets(key, wx.ComboBox(self, value=str(value)))
            elif key == 'Manuf':
                self.add_widgets(key, wx.ComboBox(self, value=str(value)))
            elif key == 'GroupeMat':
                self.add_widgets(key, wx.ComboBox(self, value=str(value)))
            else:
                self.add_widgets(key, wx.TextCtrl(self, value=str(value)))

        if self.tool.Name != "":
            self.save_btn.Enable()

        self.Fit()



    def on_save(self, event):
        print("on_save")
        saveTool(self.tool)

        print("tool :: ", self.parent)
        tools = load_tools_from_database(self.parent, self.parent.toolType )
        print("tools :: ", tools)
        """
        if self.tool:
            self.parent.list_ctrl.Select(self.parent.list_ctrl.GetFirstSelected(),0) #TODO: deselect all 
            print("Tool added:", self.tool.Name)
            index = add_line(self.parent, self.tool)
            self.parent.list_ctrl.Select(index)
        """
        #self.Destroy()  # Close the dialog after saving

    def on_create(self, event):
        self.tool.Name = self.main_sizer.GetItemCount()
        
        ts.copy_tool(self.tool)
        #print("tool :: ", self.tool)
        self.Destroy()  # Close the dialog after create tool

    