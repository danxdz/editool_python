import wx


#from gui.guiTools import getToolTypesNumber
from gui.guiTools import refreshToolList

from databaseTools import saveTool, update_tool, load_tools_from_database

#from share.save_supabase import readTools


from gui.menus_inter import MenusInter


class validateToolDialog(wx.Dialog):
    def __init__(self,parent,tool, isNew):
        title = 'Validate tool data'
        super().__init__(parent=None, title=title)
      
        self.parent = parent
        self.lang = parent.lang #0 = en, 1 = fr, 2 = pt

        self.lang = MenusInter.GetCustomLanguage()
        #get the menu text from the dictionary
        self.menu = MenusInter(self.lang)
        # define the tooltype menu
        self.m_tooltype = self.menu.get_menu("tooltype")
        self.m_save = self.menu.get_menu("save").capitalize()
        self.m_open = self.menu.get_menu("open").capitalize()
        self.m_create = self.menu.get_menu("create").capitalize()
        self.m_cancel = self.menu.get_menu("cancel").capitalize()
        self.m_all = f"{self.menu.get_menu('createToolWithHolder').capitalize()}"


        self.tool = tool
        self.ts = parent.parent.ts

        self.isNew = isNew

        self.toolData = parent.toolData

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)        

        
        self.toolPropsTextboxSizer = wx.GridSizer(rows = 0, cols = 3, hgap = 5, vgap = 5)
        self.main_sizer.Add(self.toolPropsTextboxSizer, 0, wx.ALL, 15)


        #add sizer with 5 rows
        #and add 5 square buttons for each material group P, M, M, K, S, N
        groupMat = ['P', 'M', 'K', 'N', 'S', 'H', 'O']
        groupMatName = ['Steel ', 'Stainless steel', 'Cast iron', 'Non-ferrous metal', 'Super alloy', 'Hardened Steel', 'Non ISO']
        groupMatColor = [wx.Colour(0, 100, 255), wx.Colour(226,135,67), 'red', 'green', 'brown', 'grey', 'white']

        #add space between buttons and border


        self.matSizer = wx.GridSizer(rows = 0, cols = 9, hgap = 8, vgap = 15)

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

        #add sizer to main sizer add some space

        self.main_sizer.Add(self.matSizer, 0, wx.ALL, 15  )

                    
        # Add buttons box       
        btn_sizer = wx.BoxSizer()

        self.save_btn = wx.Button(self, label=self.m_save)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(self.save_btn, 5, wx.ALL, 15)
        self.save_btn.Disable()
        
        self.open = wx.Button(self, label=self.m_open)
        self.open.Bind(wx.EVT_BUTTON, self.on_open)
        btn_sizer.Add(self.open, 5, wx.ALL, 15)

        

        self.create_btn = wx.Button(self, label=self.m_create)
        self.create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        btn_sizer.Add(self.create_btn, 5, wx.ALL, 15)
        self.create_btn.Disable()

        btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 5, wx.ALL, 15)

        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)

        self.SetSizer(self.main_sizer)
        
        self.on_load(tool)

        if self.tool.TSid != "":
            self.open.Enable()
            self.create_btn.Disable()
        else:
            self.open.Disable()
            self.create_btn.Enable()

        #resize the dialog to fit the content
        self.Fit()

        
    def on_mat_btn(self, color, bt):
        #print("on_mat_btn :: ", event.GetEventObject().GetLabel())
        #set button color
        bt.SetBackgroundColour(color)
        #set button border
        bt.SetForegroundColour('black')



    def add_widgets(self, label, widget):

        #add binding to widget and send label_text to on_change
        widget.Bind(wx.EVT_TEXT, lambda event: self.on_change(event, label))

        label_text = wx.StaticText(self, label=self.menu.get_menu(label).capitalize())
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label_text, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(widget, 0, wx.ALL, 2)
        self.toolPropsTextboxSizer.Add(sizer, 0, wx.ALL, 5)

        

    def on_load(self, tool):
      
        self.toolAttributes = tool.getAttributes()        
        #print("toolAttributes :: ", self.toolAttributes)

        #clear all widgets
        self.toolPropsTextboxSizer.Clear(True)
        self.main_sizer.Layout()
        self.main_sizer.Fit(self)

        for key, value in self.toolAttributes.items():
            #print(key, value)
            #TODO: add combobox for toolType, Manuf, GroupeMat...
            if key == 'toolType':                
                self.add_widgets(key, wx.ComboBox(self, value=str(self.toolData.tool_types_list[value]),choices=self.toolData.tool_types_list))
            elif key == 'mfr':
                self.add_widgets(key, wx.ComboBox(self, value=str(value)))
            elif key == 'cuttingMaterial':
                groupMat = ['P', 'M', 'K', 'N', 'S', 'H', 'O']
                #self.add_widgets(key, wx.ComboBox(self, value=str(value)))
            elif key == "name":
                self.add_widgets(key, wx.TextCtrl(self, value=str(value)))
                print(f"value {value}")
                if value != "":
                    self.save_btn.Enable()
                    self.create_btn.Enable()
            elif key == "id":
                pass
            else:
                self.add_widgets(key, wx.TextCtrl(self, value=str(value)))


        self.Fit()

    def on_open(self, event):
        print("open ", self.tool.name, self.tool.toolType)

        self.ts.open_file(self.tool.TSid)

        self.Destroy()

    def on_save(self, event):
        if self.tool.id != 0:
            print("updating tool ", self.tool.name, " in database")
            update_tool(self.tool)
        else:
            print("saving ", self.tool.name, self.tool.toolType , " in database")
            saveTool(self.tool)

            #testdb(self.tool)

        self.toolData.full_tools_list, existent_tooltypes = load_tools_from_database(self.toolData.selected_toolType, self.lang)

        refreshToolList(self.parent, self.toolData)
        self.parent.olvSimple.Refresh()
        
        if self.isNew:
            self.Destroy()  # Close the dialog after saving tool

        

    def on_create(self, event):
        print("create " , self.tool.name, self.tool.toolType)

        saveTool(self.tool)

        
        if not self.ts or self.ts.connected == False:
                    self.ts.Connect()
        
        self.ts.copy_tool(self, self.tool, False, False)

        self.Destroy()  # Close the dialog after create tool    

    def on_change(self, event, label_text ):
        #get the value of the widget and the textbox name changed

        #print("change",label_text, event.GetString())
        #print("on_change :: ", self)
        tool = self.tool
       
        changedValue = event.GetString()

        if label_text == 'toolType':
            #get the index of the tool type
            changedValue = self.toolData.tool_types_list.index(changedValue)
            #print("changedValue :: ", changedValue)

        #check type of value, if int or float convert it
        if label_text in ['D1', 'D2', 'D3', 'L1', 'L2', 'L3', 'Z', 'r']:
            changedValue = float(changedValue)
            #print("changedValue :: ", changedValue)

        #set object attribute with the value of the widget
        setattr(tool, label_text, changedValue)   
        self.tool = tool
