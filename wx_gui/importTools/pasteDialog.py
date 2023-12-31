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
        self.tool = tool.Tool()
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
        data = str(self.text_area.GetValue())
        len_data = len(data)

        print(len_data , " :: " ,  data)

        if len(data) > 100:
            self.tool = import_past.process_input_13999(self.text_area.GetValue(), self.parent.toolData.toolTypesList)
            #print("tool :: ", self.tool)
        else:
            #lets process data without headers
            #divide data by tab and spaces into list
            tool_data = data.split()
            for element in tool_data:
                print(element)

            #strip M from tool diameter
            self.tool.name = tool_data[0]
            self.tool.D1 = tool_data[1]
            if self.tool.D1[0] == 'M':
                #check if it is a threadMill , if its number is a threadMill, if is '6HX' one number and letters its a tap
                for letter in tool_data[3]:
                    if letter.isalpha():
                        self.tool.toolType = 5
                        break
                if self.tool.toolType == 7:
                    # 167081	M1.4	1.06	0.300	39.0	0.6	6	3.00	3	1.10
                    print("threadMill")
                    self.tool.toolType = 7
                    self.tool.D1 = self.tool.D1[2:]
                    self.tool.D2 = tool_data[2]
                    self.tool.threadPitch = tool_data[3]
                    self.tool.L3 = tool_data[4]
                    self.tool.L1 = tool_data[5]
                    self.tool.L2 = tool_data[6]
                    self.tool.D3 = tool_data[7]
                    self.tool.z = tool_data[8]
                else:
                    # 176692	M8	8.00	6H 	1.250 	90.0 	20.0 	6.00 	4.9 	2 	6.80
                    print("tap")
                    self.tool.toolType = 5
                    self.tool.D1 = tool_data[2]
                    self.tool.threadTolerance = tool_data[3]
                    self.tool.threadPitch = tool_data[4]
                    self.tool.L3 = tool_data[5]
                    self.tool.L1 = tool_data[6]
                    self.tool.D3 = tool_data[7]
                    self.tool.z = tool_data[9]

        #get all Tool attributes
        self.toolAttributes = self.tool.getAttributes()        
        print("toolAttributes :: ", self.toolAttributes)

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

        if self.tool.name != "":
            self.save_btn.Enable()

        self.Fit()



    def on_save(self, event):

        print("on_save")
        saveTool(self.tool, self.parent.toolTypesList)

        print("tool :: ", self.parent)
        tools = load_tools_from_database(self.tool.toolType)

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
        self.tool.name = self.main_sizer.GetItemCount()
        
        ts.copy_tool(self.tool)
        #print("tool :: ", self.tool)
        self.Destroy()  # Close the dialog after create tool    