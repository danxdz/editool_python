import wx

import sys

import databaseTools as db
import import_xml_wx as iXml
import ts
from export_xml_wx import create_xml_data


class EditDialog(wx.Dialog):
    def __init__(self, tool):
        title = f'Editing "{tool.Name}"'
        super().__init__(parent=None, title=title)
        self.tool = tool
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Replace these lines with the attributes from your Tool class
        self.name_text = wx.TextCtrl(self, value=self.tool.Name)
        self.add_widgets('Name', self.name_text)

        self.type_text = wx.TextCtrl(self, value=self.tool.Type)
        self.add_widgets('Type', self.type_text)

        # Repeat the above pattern for other attributes...

        btn_sizer = wx.BoxSizer()
        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 0, wx.ALL, 5)
        btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(self.main_sizer)


    def add_widgets(self, label, widget):
        label_text = wx.StaticText(self, label=label)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(label_text, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(widget, 0, wx.ALL | wx.CENTER, 5)
        self.main_sizer.Add(sizer, 0, wx.ALL | wx.CENTER, 5)

    def on_save(self, event):
        # Update the Tool object with the edited values
        self.tool.Name = self.name_text.GetValue()
        self.tool.Type = self.type_text.GetValue()
        # Repeat the above pattern for other attributes...

        # Add your save logic here
        # For example, you might want to update the database with the changes
        # db.update_tool(self.tool)
        self.Destroy()  # Close the dialog after saving

class ToolManagerUI(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Tool Manager')
        self.panel = ToolPanel(self, self)
        self.create_menu()
        self.SetSize(800, 800)
        self.Centre()
        self.Show()
        self.tools_list = []

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        open_xml = file_menu.Append(
            wx.ID_ANY, 'Open xml file', 
            'open a xml file with tool data'
        )
        open_zip = file_menu.Append(
            wx.ID_ANY, 'Open zip file', 
            'open a zip file with tool data'
        )
        exp_xml = file_menu.Append(
            wx.ID_ANY, 'Export XML file', 
            'export tool data into XML file'
        )
        exit = file_menu.Append(
            wx.ID_ANY, "exit", "close app"
        )
        menu_bar.Append(file_menu, '&File')
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_xml,
            source=open_xml,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.on_open_zip,
            source=open_zip,
        )
        self.Bind(
            event=wx.EVT_MENU, 
            handler=self.export_xml,
            source=exp_xml,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.close_app,
            source=exit
        )
        self.SetMenuBar(menu_bar)

        #add icon to toolbar with tooltip

        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((15,28))
        self.toolbar.AddTool(1, "Exit", wx.Bitmap("icons/fr2t.png"))

        self.toolbar.AddTool(2, "Open", wx.Bitmap("icons/frto.png"))
        self.toolbar.AddTool(3, "Save", wx.Bitmap("icons/frhe.png"))

        self.toolbar.Realize()
        
        #self.toolbar.Bind(wx.EVT_TOOL, self.fr2t, id=1)
        #self.toolbar.Bind(wx.EVT_TOOL, self.frto, id=2)
        #self.toolbar.Bind(wx.EVT_TOOL, self.frhe, id=3)
    
    
    def export_xml(self, event):
        print("export_xml")
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tool = self.panel.get_selected_item()
        print("tool :: ", tool)
        xml_data = create_xml_data(tool)
        #iXml.save_file(self, title, wcard, xml_data)

    def close_app(event, handle):
        print("exit",event.Title, handle, sep=" :: ")
        sys.exit()        
    
    def on_open_xml(self, event):
        title = "Choose a XML file:"
        wcard ="XML files (*.xml)|*.xml"
        tool = iXml.open_file(self, title, wcard)
        print("tool %s", tool)
        if tool:
            print("Tool added:", tool.Name)
            index = self.panel.add_line(tool)
            #self.tools_list.append(tool)
            self.panel.list_ctrl.Select(index)

    def on_open_zip(self, event):
        title = "Choose a Zip file:"
        wcard ="Zip files (*.zip)|*.zip"
        iXml.open_file(self, title, wcard)     

class ToolPanel(wx.Panel):    
    def __init__(self, parent, main_frame):
        super().__init__(parent)
        self.main_frame = main_frame


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.row_obj_dict = {}


        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, 300), 
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )

        #enable alternating row colours
        #self.list_ctrl.EnableAlternateRowColours(enable=True)

        self.list_ctrl.Enable(True)

        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.get_focus, self.list_ctrl)
        self.list_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.right_click, self.list_ctrl)

        self.add_columns()

        
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)        

        #need to change to array of dropboxs so i can have multiple dropboxs
        self.dropbox_contrainer = wx.BoxSizer(wx.HORIZONTAL)
        self.D1_dropbox = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.dropbox_contrainer.Add(self.D1_dropbox, 0, wx.ALL | wx.CENTER, 5)
        self.L1_dropbox = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.dropbox_contrainer.Add(self.L1_dropbox, 0, wx.ALL | wx.CENTER, 5)
        self.L2_dropbox = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.dropbox_contrainer.Add(self.L2_dropbox, 0, wx.ALL | wx.CENTER, 5)
        self.Z_dropbox = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        self.dropbox_contrainer.Add(self.Z_dropbox, 0, wx.ALL | wx.CENTER, 5)

        main_sizer.Add(self.dropbox_contrainer, 0, wx.ALL | wx.CENTER, 5)
        
        self.D1_dropbox.Bind(wx.EVT_COMBOBOX, lambda event: self.on_select(event, self.filter_D1,"D1", self.L1_dropbox, self.L2_dropbox, self.Z_dropbox))
        self.L1_dropbox.Bind(wx.EVT_COMBOBOX, lambda event: self.on_select(event, self.filter_L1,"L1", self.L2_dropbox, self.Z_dropbox))




        edit_button = wx.Button(self, label='Edit')
        edit_button.Bind(wx.EVT_BUTTON, self.on_menu_click)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)        
        self.SetSizer(main_sizer)

        self.popup_menu = wx.Menu()
        self.popup_menu.Append(0, "Create")
        self.popup_menu.Append(1, "Edit")
        self.popup_menu.Append(2, "Delete")
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=0)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=1)
        self.popup_menu.Bind(wx.EVT_MENU, self.on_menu_click, id=2)

        self.load_tools()

    def add_columns(self):
        self.list_ctrl.InsertColumn(0, "n" , width=50)
        self.list_ctrl.InsertColumn(1, 'name', width=100)
        self.list_ctrl.InsertColumn(2, 'D1', width=50)
        self.list_ctrl.InsertColumn(3, 'L1', width=50)
        self.list_ctrl.InsertColumn(4, 'D2', width=50)
        self.list_ctrl.InsertColumn(5, 'L2', width=50)
        self.list_ctrl.InsertColumn(6, 'D3', width=50)
        self.list_ctrl.InsertColumn(7, 'L3', width=50)
        self.list_ctrl.InsertColumn(8, 'type', width=50)



    def on_select(self, event, filter_func, filter, *dropboxes):
        print("on_select :: "  + event.GetString() +  " :: " +  filter )
        self.list_ctrl.ClearAll()
        self.add_columns()
        for dropbox in dropboxes:
            dropbox.Clear()

        new_tool_list = []
        if event.GetString() == " ": # blank
            value = 0
        else:
            value = float(event.GetString())

        print(" ********************************* value :: ", value)
        for tool in self.row_obj_dict.values():
            if value == 0:  # blank
                print("value vide :: ", value)
                self.add_line(tool)
                new_tool_list.append(tool)
            else:
                print("value :: ", value , " :: ", tool.D1)
                if filter == "D1":
                    flt = tool.D1
                elif filter == "L1":
                    flt = tool.L1
                if (flt == value):
                    print("adding tool :: ", tool.Name)
                    filter_func(tool,value)
                    self.add_line(tool)
                    new_tool_list.append(tool)

        for tool in new_tool_list:
            print("filter func: ", filter_func)
            filter_func(tool,value)

        # Após aplicar todos os filtros, atualize a lista
        self.list_ctrl.Refresh() 

    def filter_D1(self, tool, value):
            self.fill_dropboxs(tool.L1, self.L1_dropbox)
            self.fill_dropboxs(tool.L2, self.L2_dropbox)
            self.fill_dropboxs(tool.NoTT, self.Z_dropbox)

    def filter_L1(self, tool, value):
            self.fill_dropboxs(tool.D1, self.D1_dropbox)
            self.fill_dropboxs(tool.L2, self.L2_dropbox)
            self.fill_dropboxs(tool.NoTT, self.Z_dropbox)



    def get_selected_item(self):
        index = self.list_ctrl.GetFirstSelected()
        print("index :: ", index)
        if index > -1:
            return self.row_obj_dict.get(index)
        else:
            return None



    def get_focus(self, event):
        ind = self.list_ctrl.GetFocusedItem()
        print ("GotFocus :: " , self.row_obj_dict[ind].Name)

       

    def right_click(self, event):
        count = self.list_ctrl.GetSelectedItemCount()
        #gets the position of the mouse click
        pos = self.list_ctrl.HitTest(event.GetPosition())

        if count < 2:
            #deselects all the items
            self.list_ctrl.Select(-1, 0)
            #selects the item clicked
            self.list_ctrl.Select(pos[0])

        #gets the index of the item clicked
        ind = self.list_ctrl.GetFirstSelected()
        print (ind)
        #gets the item clicked
        item = self.list_ctrl.GetItem(ind)
        
        print("RMC :: ",item,  " :: ", count , pos)

        self.show_popup(event)

    def fill_dropboxs(self, tool, dropbox):
                #add the D1 value to the dropbox if it is not already there
        items = dropbox.GetItems()
        d1 = str(tool)
        if str(d1) not in items:
            print(d1, " :: " , items)
            dropbox.Append(d1)

        #order the dropbox items remeber they are strings, so make sure to convert to real numbers
        items = dropbox.GetItems()
        #print("items :: ", items)
        #first item must be blank we dont want to sort that
        if items[0] == " ":
            items.pop(0)
        #print("items :: ", items)
        items.sort(key=float)
        #append the blank item back to the list to make it the first item
        items.insert(0, " ")
        
        dropbox.SetItems(items)
        #print("items :: ", items)


    def add_line(self, tool):
        index = self.list_ctrl.GetItemCount()

        self.row_obj_dict[index] = tool

        print("adding tool line :: ", index, " :: ", tool.Name)

        index = self.list_ctrl.InsertItem(index, str(index + 1))
        self.list_ctrl.SetItem(index, 1, tool.Name)
        self.list_ctrl.SetItem(index, 2, str(tool.D1))
        self.list_ctrl.SetItem(index, 3, str(tool.L1))
        self.list_ctrl.SetItem(index, 4, str(tool.D2))
        self.list_ctrl.SetItem(index, 5, str(tool.L2))
        self.list_ctrl.SetItem(index, 6, str(tool.D3))
        self.list_ctrl.SetItem(index, 7, str(tool.L3))
        self.list_ctrl.SetItem(index, 8, str(tool.Type))

        return index



    def create_tool(self, index):
        print("create tool :: ", self.row_obj_dict[index].Name)
        tool = self.row_obj_dict[index]
        
        #ts.conn()
        ts.copy_tool(tool)
        print("tool :: ", tool)

    def on_menu_click(self, event):
        id = event.GetId()
        
        print('in on_edit :: ', id)
        count = self.list_ctrl.GetSelectedItemCount()
        
        ind = self.list_ctrl.GetFirstSelected()
        print (ind)
        #gets the item clicked
        item = self.list_ctrl.GetItem(ind)

        print("EDIT :: ",item,  " :: ", count )

        print("count :: ", count)
        if count > 1:
            print("multiple items selected")
        else:
            print("single item selected")

        print("selected item :: ", self.get_selected_item())

        if id == 0:
            print("Create")           
            
            for i in range(count):
                self.list_ctrl.SetItemBackgroundColour(item=i+ind, col='#f0f2f0')
                self.list_ctrl.SetItemTextColour(item=i+ind, col='#000000')
                self.list_ctrl.RefreshItem(i+ind)
                self.create_tool(i+ind)
            
        elif id == 1:
            print("Edit")
            EditDialog(self.get_selected_item()).ShowModal()

        elif id == 2:
            print("Delete")
            self.delete_selected_item()


    def load_tools(self):
        self.list_ctrl.ClearAll
        tools = db.load_tools_from_database(self)

        tools = reversed(tools)

        self.D1_dropbox.Append(str(" "))
        self.L1_dropbox.Append(str(" "))
        self.L2_dropbox.Append(str(" "))
        self.Z_dropbox.Append(str(" "))

        for tool in tools:
            self.add_line(tool)

            dropbox = self.D1_dropbox
            self.fill_dropboxs(tool.D1, dropbox)    
            dropbox = self.L1_dropbox
            self.fill_dropboxs(tool.L1, dropbox)
            dropbox = self.L2_dropbox
            self.fill_dropboxs(tool.L2, dropbox)
            dropbox = self.Z_dropbox
            self.fill_dropboxs(tool.NoTT, dropbox)

    #show popup menu
    def show_popup(self, event):
        pos = event.GetPosition()        
        self.PopupMenu(self.popup_menu, pos)
