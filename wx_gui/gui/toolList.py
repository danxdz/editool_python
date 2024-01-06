
import wx

from importTools.validateImportDialogue import validateToolDialog

from gui.guiTools import add_columns
from gui.guiTools import refreshToolList
from gui.guiTools import toolDetailsPanel

from databaseTools import delete_selected_item

from ts import copy_tool, copy_holder, get_tool_TSid

RW = 520 # ruler width
RM = 10  # ruler margin
RH = 220  # ruler height

class ToolList(wx.Panel):    
    def __init__(self, parent, toolData):
        super().__init__(parent=parent)

        self.font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.font_name = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
            


        self.parent = parent
        
        #initialize the tool list
        self.tool_labels = {}

        self.toolData = toolData
        self.selected_tool = self.toolData.full_tools_list[0]


        #create the sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.toolView = wx.Panel(self, size=(550, 250))
        self.sizer.Add(self.toolView, 0, wx.ALL, 5)

        self.toolView.Bind(wx.EVT_PAINT, self.OnPaint)

        #this is the list control that will hold the tools list
        self.list_ctrl = wx.ListCtrl(
            self, size=(550, 200),
            style=wx.LC_REPORT | wx.BORDER_SIMPLE | wx.LC_VRULES 
        )   

   
        #this is needed to allow the lines oflist control to be selected
        self.list_ctrl.Enable(True)

        #bind the events to the list control
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.toolSelected, self.list_ctrl, id=wx.ID_ANY)
        #right click event
        self.list_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.right_click, self.list_ctrl)
        #double left click event
        self.list_ctrl.Bind(wx.EVT_LEFT_DCLICK, self.db_click, self.list_ctrl)

        add_columns(self)

        
        refreshToolList(self,self.toolData.full_tools_list, -1)

        if len(toolData.full_tools_list) > 0:
            tool = toolData.full_tools_list[0]
   
        
        #add the list control to the sizer
        self.sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        
        #create popup menu
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, "Create tool")
        self.popup_menu.Append(1, "Create tool with holder")
        self.popup_menu.Append(2, "Edit")
        self.popup_menu.Append(3, "Delete")
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(4, "Export")
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click)


    def toolSelected(self, event):
        tool = self.toolData.full_tools_list[self.list_ctrl.GetFirstSelected()]  
        toolTypeName = self.toolData.tool_types_list[tool.toolType]           
        self.parent.statusBar.SetStatusText(f"tool selected: {tool.name} :: {toolTypeName}")

        if tool.name:
            print ("tool selected: ", tool.name , " :: ", toolTypeName )
            self.Refresh()
            self.selected_tool = tool


            

        else:
            print("error :: tool selected:: ", tool)

    


    def OnPaint(self, e):
        tool = self.selected_tool
        print("OnPaint", tool.name)
        dc = wx.PaintDC(self.toolView)

        brush = wx.Brush(wx.Brush(wx.Colour(240,240,240), wx.BRUSHSTYLE_SOLID))
        dc.SetBrush(brush)
        dc.SetPen(wx.Pen(wx.Colour((210,210,250)))) 

        dc.DrawRectangle(0, 0, RW+2*RM, RH)
        dc.SetFont(self.font_name)

        dc.SetPen(wx.Pen('#0f0f0f'))
        dc.SetTextForeground(wx.Colour("black"))
        w, h = dc.GetTextExtent(str(tool.name))
        dc.DrawText(str(tool.name), int(RM), 11)

        def draw_rectangle(x, y, width, height):
                dc.DrawRectangle(int(x), int(y), int(width), int(height))


         # Calculate scale factors
        w = 540
        start_y = 150
        scale_width = (w -1) / tool.L3

        # Scale tool attributes
        scaled_values = {
            'D1': int(tool.D1 * scale_width),
            'D2': int(tool.D2 * scale_width) if tool.D2 else 0,
            'D3': int(tool.D3 * scale_width),
            'L1': int(tool.L1 * scale_width),
            'L2': int(tool.L2 * scale_width) if tool.L2 else 0,
            'L3': int(tool.L3 * scale_width),
        }

        for key, value in scaled_values.items():
            print(key, value)

        # Draw rectangles

        dc.SetPen(wx.Pen(wx.Colour("drak gray")))
        dc.SetBrush(wx.Brush(wx.Colour("gray"), wx.BRUSHSTYLE_SOLID))
        # Need to center the tool neck, by find the dif between d1 and d2 and divide by 2
        dif = (scaled_values['D1'] - scaled_values['D2']) / 2
        draw_rectangle(scaled_values['L1']-1, start_y + dif, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2'])
        draw_rectangle(scaled_values['L2']-1, start_y, scaled_values['L3']-scaled_values['L2']+1, -scaled_values['D3'])

        dc.SetPen(wx.Pen(wx.Colour("orange")))
        dc.SetBrush(wx.Brush(wx.Colour("yellow"), wx.BRUSHSTYLE_SOLID))
        draw_rectangle(0, start_y, scaled_values['L1']+1, -scaled_values['D1'])

        # Draw axis line
        dc.SetPen(wx.Pen(wx.Colour("red"), 3, wx.DOT_DASH))
        dc.DrawLine(0, start_y, 540, start_y)


        # Draw tool
        dc.SetPen(wx.Pen('#0f0f0f'))
        dc.SetFont(self.font)
        
        #find the middle of the tool l3, so we can draw the text in the middle of tool corps
        m_l1 = int((scaled_values['L1']-0)/2)+0
        m_l2 = int((scaled_values['L2']-scaled_values['L1'])/2)+scaled_values['L1']
        m_l3 = int((scaled_values['L3']-scaled_values['L2'])/2)+scaled_values['L2']


        dc.SetTextForeground(wx.Colour("black"))
        dc.DrawText('D1', m_l1-15, start_y+5)
        dc.DrawText('L1', m_l1+15, start_y+5)
        dc.DrawText('D2', m_l2-15, start_y+5)
        dc.DrawText('L2', m_l2+15, start_y+5)
        dc.DrawText('D3', m_l3-15, start_y+5)
        dc.DrawText('L3', m_l3+15, start_y+5)

        dc.SetTextForeground(wx.Colour("orange"))
        dc.DrawText(str(tool.D1), m_l1-15, start_y+20)
        dc.DrawText(str(tool.L1), m_l1+15, start_y+20)
        dc.DrawText(str(tool.D2), m_l2-15, start_y+20)
        dc.DrawText(str(tool.L2), m_l2+15, start_y+20)
        dc.DrawText(str(tool.D3), m_l3-15, start_y+20)
        dc.DrawText(str(tool.L3), m_l3+15, start_y+20)
                    
        '''# Draw tool lines
        dc.SetPen(wx.Pen('#0f0f0f'))
        dc.DrawLine(0, 0, 0, scaled_values['D1'])
        dc.DrawLine(0, scaled_values['D1'], scaled_values['L1'], scaled_values['D1'])
        dc.DrawLine(scaled_values['L1'], scaled_values['D1'], scaled_values['L1'], scaled_values['D2'])
        dc.DrawLine(scaled_values['L1'], scaled_values['D2'], scaled_values['L2'], scaled_values['D2'])
        dc.DrawLine(scaled_values['L2'], scaled_values['D2'], scaled_values['L2'], scaled_values['D3'])
        dc.DrawLine(scaled_values['L2'], scaled_values['D3'], scaled_values['L3'], scaled_values['D3'])
        dc.DrawLine(scaled_values['L3'], scaled_values['D3'], scaled_values['L3'], 0)
        dc.DrawLine(scaled_values['L3'], 0, 0, 0)'''
        


       
    def db_click(self, event):
        print("edit tool: ",  self.list_ctrl.GetFirstSelected())
        i = self.list_ctrl.GetFirstSelected()

        tool = self.toolData.full_tools_list[i]

        #EditDialog(self,tool, self.toolData.tool_types_list).ShowModal()
        validateToolDialog(self, tool).ShowModal()
      


    def right_click(self, event):
        count = self.list_ctrl.GetSelectedItemCount()
        #gets the position of the mouse click
        pos = self.list_ctrl.HitTest(event.GetPosition())

        if count < 2:
            #deselects all the items
            self.list_ctrl.Select(-1, 0)
            #selects the item clicked
            self.list_ctrl.Select(pos[0])       

        self.show_popup(event)


    def on_menu_click(self, event):
        id = event.GetId()        
        print('on_menu_click :: ', id)

        count = self.list_ctrl.GetSelectedItemCount()        
        ind = self.list_ctrl.GetFirstSelected()

        if count > 1:
            print("multiple items selected")
            for i in range(count):
                print("selected item :: ")
        else:
            print("single item selected")


        for i in range(count):
            modif_tooltype = -1
            if count > 1:
                modif_tooltype = self.toolData.full_tools_list[i+ind].toolType

            if id == 0:                
                print("floatMenu :: Create")      
                #create tool :: false = no holder 
                print("create tool :: ", self.toolData.full_tools_list[i+ind].name)
                copy_tool(self.toolData.full_tools_list[i+ind], False)
                refreshToolList(self,self.toolData.full_tools_list, self.toolData.full_tools_list[i+ind].toolType)
            if id == 1:                
                print("floatMenu ::  Create with holder")     
                #create tool :: true = holder
                print("create holder for :: ", self.toolData.full_tools_list[i+ind].name)
                #id = ts.get_tool_TSid(tool)
                copy_holder(None, get_tool_TSid(self.toolData.full_tools_list[i+ind]))
            elif id == 2:
                print("floatMenu :: Edit :: ", self.toolData.full_tools_list[i+ind].name )
                validateToolDialog(self, self.toolData.full_tools_list[i+ind]).ShowModal()
            elif id == 3:
                print("floatMenu :: Delete")
                delete_selected_item(self.GetParent(),i+ind)
                self.list_ctrl.DeleteAllItems()
            
        
        refreshToolList(self,self.toolData.full_tools_list, modif_tooltype )


    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)