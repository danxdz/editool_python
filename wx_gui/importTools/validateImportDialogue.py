import wx
import ts as ts

from databaseTools import saveTool

class validateToolDialog(wx.Dialog):
    def __init__(self,parent,tools):
        title = 'Validate tool data'
        super().__init__(parent=None, title=title)
      
        self.parent = parent
        self.tools = tools

        self.newTools = []

        self.toolTypes = parent.toolTypesList
        self.toolTypesNumber = parent.toolData.toolTypesNumbers

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        

        #add sizer with 5 rows
        #and add 5 square buttons for each material group P, M, M, K, S, N
        groupMat = ['P', 'M', 'K', 'N', 'S', 'H', 'O']
        groupMatName = ['Steel ', 'Stainless steel', 'Cast iron', 'Non-ferrous metal', 'Super alloy', 'Hardened Steel', 'Non ISO']
        groupMatColor = ['blue', 'orange', 'red', 'green', 'brown', 'grey', 'white']

        self.matSizer = wx.GridSizer(rows = 0, cols = 9, hgap = 1, vgap = 15)

        #add empty button
        self.allMatBtn = wx.ToggleButton(self, label="all", size=(40, 40))
        self.allMatBtn.SetToolTip('select all')
        self.matSizer.Add(self.allMatBtn, 0, wx.CENTER)


        #add buttons with material group icons
        for i, mat in enumerate(groupMat):
            self.matBtn = wx.ToggleButton(self, label=mat, size=(40, 40))
            self.matBtn.SetBackgroundColour(groupMatColor[i])
            #self.matBtn.SetBitmap(wx.Bitmap(f'icons/materials/{mat}.png'))
            self.matBtn.Bind(wx.EVT_BUTTON, self.on_mat_btn(groupMatColor[i], self.matBtn), id=i)
            self.matSizer.Add(self.matBtn, 0, wx.CENTER)
            self.matBtn.SetLabel(mat)
            self.matBtn.SetToolTip(groupMatName[i])
            #self.matBtn.SetForegroundColour('white')


        #add empty button to clear selection
        self.clearMatBtn = wx.ToggleButton(self, label="none", size=(40, 40))
        self.clearMatBtn.SetToolTip('clear selection')
        self.matSizer.Add(self.clearMatBtn, 0, wx.CENTER)


        self.main_sizer.Add(self.matSizer, 0, wx.CENTER)

        self.textboxSizer = wx.GridSizer(rows = 0, cols = 3, hgap = 5, vgap = 5)
        self.main_sizer.Add(self.textboxSizer, 0, wx.Center)
                    
        # Add buttons box       
        btn_sizer = wx.BoxSizer()

        self.save_btn = wx.Button(self, label='Save')
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(self.save_btn, 5, wx.ALL, 15)
        self.save_btn.Disable()

        self.create_btn = wx.Button(self, label='Create')
        self.create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        btn_sizer.Add(self.create_btn, 5, wx.ALL, 15)
        self.create_btn.Disable()

        btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 5, wx.ALL, 15)

        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(self.main_sizer)


        self.on_load(tools)
        #resize the dialog to fit the content
        self.Fit()
        
    def on_mat_btn(self, color, bt):
        #print("on_mat_btn :: ", event.GetEventObject().GetLabel())
        print("on_mat_btn :: ", color)
        #set button color
        bt.SetBackgroundColour(color)
        #set button border
        bt.SetForegroundColour('white')



    def add_widgets(self, label, widget):
        
        label_text = wx.StaticText(self, label=label)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label_text, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(widget, 0, wx.ALL, 2)
        self.textboxSizer.Add(sizer, 0, wx.ALL, 5)

    def on_load(self, tools):
      
        #get all Tool attributes
        for tool in tools:
            self.toolAttributes = tool.getAttributes()        
            #print("toolAttributes :: ", self.toolAttributes)

            #clear all widgets
            self.textboxSizer.Clear(True)
            self.main_sizer.Layout()
            self.main_sizer.Fit(self)

            for key, value in self.toolAttributes.items():
                #print(key, value)
                #TODO: add combobox for toolType, Manuf, GroupeMat...
                if key == 'toolType':
                    
                    self.add_widgets(key, wx.ComboBox(self, value=str(self.toolTypes[value]),choices=self.toolTypes))
                elif key == 'Manuf':
                    self.add_widgets(key, wx.ComboBox(self, value=str(value)))
                elif key == 'GroupeMat':
                    self.add_widgets(key, wx.ComboBox(self, value=str(value)))
                elif key == "Name":
                    self.add_widgets(key, wx.TextCtrl(self, value=str(value)))
                    print(f"value {value}")
                    if value != "":
                        self.save_btn.Enable()
                        self.create_btn.Enable()
                        self.newTools.append(tool)

                else:
                    self.add_widgets(key, wx.TextCtrl(self, value=str(value)))


            self.Fit()


    def on_save(self, event):

        print("on_save", self.newTools)
        for tool in self.newTools:
            print("tool :: ", tool)
            saveTool(tool,self.toolTypes) 
        
        #self.Destroy()  # Close the dialog after saving

    def on_create(self, event):
        print("on_create")

        self.Destroy()  # Close the dialog after create tool    