# Autor: Carlo Pii
import wx

from gui.guiTools import load_masks


class toolSetupPanel(wx.Dialog):
    def __init__(self, parent):
        title = 'Tool setup'
        super().__init__(parent=None, title=title)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.parent = parent

        self.toolparams_sizerGrid = wx.GridSizer(0, 3, 0, 0)

        self.toolData = self.parent.toolData
        
        #add tool setup panel to the dialog
        masks = load_masks()
        tsmodels = self.toolData.ts_models

        print("tsmodels :: ", len(tsmodels))

        #add tooltypes icons to the dialog
        #self.main_sizer.Add(tooltypesButtons(self),  0, wx.ALL, 5)
    
         
        self.mask_textctrls = []  # Add this line to create a list to hold the TextCtrl widgets
        self.ts_models = []


        for i, mask in enumerate(masks):
            #add static text to gridbag sizer
            self.toolparams_boxs = wx.BoxSizer(wx.VERTICAL)
            #set size of the box
            self.toolparams_boxs.SetMinSize((300, 40))

            #align text to the center   
                
            self.toolparams_boxs.Add(wx.StaticText(self, label=self.toolData.tool_types_list[i]), 0, wx.ALL | wx.CENTER , 5)

            mask_textctrl = wx.TextCtrl(self ,value=mask)  # Add this line to create the TextCtrl widget
            self.toolparams_boxs.Add(mask_textctrl , 0, wx.ALL|wx.EXPAND | wx.CENTER , 5)  # Use the TextCtrl widget here
            
            tsmodels_textctrl = wx.TextCtrl(self ,value=tsmodels[i])  # Add this line to create the TextCtrl widget
            self.toolparams_boxs.Add(tsmodels_textctrl , 0, wx.ALL|wx.EXPAND | wx.CENTER , 5)  # Use the TextCtrl widget here
    
            self.mask_textctrls.append(mask_textctrl)  # Add the TextCtrl widget to the list
            self.mask_textctrls.append(tsmodels_textctrl)  # Add the TextCtrl widget to the list
            self.toolparams_sizerGrid.Add(self.toolparams_boxs, 0, wx.ALL |wx.EXPAND | wx.CENTER , 5)

        self.main_sizer.Add(self.toolparams_sizerGrid, 0, wx.ALL |wx.EXPAND | wx.CENTER , 5)

        # Add save and cancel buttons        
        btn_sizer = wx.BoxSizer()
        save_btn = wx.Button(self, label='save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 5, wx.ALL, 15)

        #add close button
        close_btn = wx.Button(self, label='close')
        close_btn.Bind(wx.EVT_BUTTON, self.close)
        btn_sizer.Add(close_btn, 5, wx.ALL, 15)

        self.main_sizer.Add(btn_sizer, 0, wx.CENTER | wx.ALL, 15)
        self.SetSizer(self.main_sizer)
        #resize the dialog to fit the content
        self.Fit()


    def close(self, event):
        print("close :: ")
        self.Destroy()
        
    def on_save(self, event):
        print("on_save :: ")
        #save masks to text file
        #get text from textctrls
        masks = []

        #need to divide the list in two lists
        #one for masks and one for tsmodels
        for i, mask_textctrl in enumerate(self.mask_textctrls):
            if i % 2 == 0:
                mask = mask_textctrl.GetValue()
                masks.append(mask+"\n")
            else:
                tsmodel = mask_textctrl.GetValue()
                #masks.append(tsmodel+"\n")
        
        with open("toolsetup.txt", "w", encoding='utf-8') as f:
            print("masks :: ", len(masks))

            f.writelines(masks)
        f.close()

    def on_load(self,masks):
        print("on_load :: ")
        load_masks(masks)

        

        

