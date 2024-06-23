import logging
import wx
import inspect
import os
import json
import clr
clr.AddReference("System")
from System.Collections.Generic import List 

# Import the TopSolidAPI class from the top_solid_api module
from topsolid_api import TopSolidAPI



class TopSolidGUI(wx.Frame):
    def __init__(self, parent, title):
        super(TopSolidGUI, self).__init__(parent, title=title, size=(800, 600))
        #self.topSolid = None  # TopSolidAPI instance
        self.topSolid = TopSolidAPI()
        

        self.menu_items = {}

        #add a status bar 
        self.CreateStatusBar()
        #add a menu bar
        menu_bar = wx.MenuBar()
        #add a file menu
        file_menu = wx.Menu()
        #add a menu item to file menu
        file_menu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        #add a listener to menu item
        self.Bind(wx.EVT_MENU, self.on_close, id=wx.ID_EXIT)
        #add file menu to menu bar
        menu_bar.Append(file_menu, "File")

        #add meni Pdm
        pdm_meth = self.topSolid.ts.Pdm
        doc_meth = self.topSolid.ts.Documents
        #add a menu to pdm
        pdm_menu = wx.Menu()
        doc_menu = wx.Menu()

        
        #call function to get all methods from pdm and doc groupe by first letter
        for letter in "abcdefghijklmnopqrstuvwxyz":
            if any(attribute.lower().startswith(letter) for attribute in dir(pdm_meth)):
                submenu = wx.Menu()
                for attribute in dir(pdm_meth):
                    if attribute.lower().startswith(letter):
                        menu_item = submenu.Append(wx.ID_ANY, attribute)
                        self.menu_items[menu_item.GetId()] = attribute
                        submenu.Bind(wx.EVT_MENU, self.on_menu, menu_item)
                pdm_menu.AppendSubMenu(submenu, letter.upper())

            if any(attribute.lower().startswith(letter) for attribute in dir(doc_meth)):
                submenu = wx.Menu()
                for attribute in dir(doc_meth):
                    if attribute.lower().startswith(letter):
                        menu_item = submenu.Append(wx.ID_ANY, attribute)
                        self.menu_items[menu_item.GetId()] = attribute
                        submenu.Bind(wx.EVT_MENU, self.on_menu, menu_item)
                doc_menu.AppendSubMenu(submenu, letter.upper())

        menu_bar.Append(pdm_menu, "Pdm")
        menu_bar.Append(doc_menu, "Documents")






        #add menu bar to frame
        self.SetMenuBar(menu_bar)

        self.pdm = None
        self.doc_id = None

        #add text to status bar
        self.SetStatusText("TopSolid API GUI")

        self.open_projects = None

        self.all_projects = None
        self.current_project = None

        self.panel = wx.Panel(self)
        self.create_widgets()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.right_clicked_button = None 

        #add a listener to when window  get focus
        self.Bind(wx.EVT_ACTIVATE, self.project_status_refresh)
        #add a listener when item get double clicked
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_tree_dclick)
        #self.Bind(wx.EVT_ACTIVATE, self.refresh_tree)
        self.refresh_tree()

    def on_tree_dclick(self, event):
        item = event.GetItem().GetText()
        print(item)        

    def on_tree_select(self, event):
        item = event.GetItem()
        print(f"Selected item: {self.tree.GetItemText(item)}")
        #get data from selected item
        data = self.tree.GetItemData(item)
        if data:
            print(f"Data: {data}")

    def refresh_tree(self, event=None):
        # Clear the tree
        self.tree.DeleteAllItems()
        
        # Get checked boxes values
        show_all_projects = self.show_all_projects.GetValue()
        show_all_files = self.show_all_files.GetValue()
        print(show_all_projects, show_all_files)

        # Add the root item
        root = self.tree.AddRoot("TopSolid Projects")
        
        # Get projects based on checkbox values
        all_projects = (self.topSolid.ts.Pdm.GetProjects(True, False) 
                        if show_all_projects 
                        else self.topSolid.get_open_projects())
        
        # Add the projects as children of the root
        for project in all_projects:
            project_name = self.topSolid.get_name(project)
            project_item = self.tree.AppendItem(root, project_name, data=project)
            
            # Add the project's constituents as children of the project
            if show_all_files:
                try:
                    _, constituents = self.topSolid.get_constituents(project, True)
                    for constituent in constituents:
                        self.get_folder_consts(constituent, project_item)
                except Exception as e:
                    print(f"Error {e} - {self.topSolid.get_name(constituent)}")

        # Expand the tree's first level (projects)
        self.tree.Expand(root)

    def get_folder_consts(self, constituent, parent_item):
        if isinstance(constituent, tuple):
            # It's a folder with its contents
            folder, contents = constituent
            if isinstance(folder, str):
                folder_name = folder
            else:
                folder_name = self.topSolid.get_name(folder)
            folder_item = self.tree.AppendItem(parent_item, folder_name, data="Folder")
            for content in contents:
                self.get_folder_consts(content, folder_item)
        else:
            # It's a file
            file_type = self.topSolid.get_type(constituent)
            if file_type:
                self.tree.AppendItem(parent_item, self.topSolid.get_name(constituent), data=constituent)


            
    def project_status_refresh(self, event):
        # Check if the frame is getting focus
        if event.GetActive():
            # Get open projects and update the GUI accordingly
            self.open_projects = self.topSolid.get_open_projects()
            if self.open_projects:
                self.open_projects_status.SetLabel("open projects: " + str(len(self.open_projects)))
                self.SetStatusText("Open projects: " + str(len(self.open_projects)))
            else:
                self.open_projects_status.SetLabel("open projects: No Open Projects")
                self.SetStatusText("Open projects: No Open Projects")
            
            self.topSolid.get_current_project()
            if self.topSolid.current_proj_name:
                self.project_status.SetLabel("active project: " + self.topSolid.current_proj_name)
            else:
                self.project_status.SetLabel("active project: No Project Open")

        event.Skip() 
    
    def on_tree_right_click(self, event):
        item = event.GetItem()
        
        if item:
            #create PdmObjectId from item data
            #public PdmObjectId(string inPdmObjectId)
            pdm_id = self.tree.GetItemData(item)
            if pdm_id is not str and pdm_id != "Folder" and pdm_id:
                proj = self.topSolid.ts.Pdm.GetProject(pdm_id)
                doc = self.topSolid.ts.Documents.GetDocument(pdm_id)
       
                print(f'Right clicked item: {self.tree.GetItemText(item)} - {self.topSolid.get_name(doc)} - {self.topSolid.get_name(proj)} - {proj.Id} - {doc.PdmDocumentId}')

            self.tree.SelectItem(item)
            self.PopupMenu(self.ts_tree_menu(pdm_id))
    
   
    def get_real_value_for_param(self, param, docId=None):
        # Este método deve ser ajustado para retornar valores reais para os parâmetros
        if param.name == 'inObjectId' or  param.name == 'inProjectId' or param.name == 'inProjectFolderId':
            # return object id
            return docId        
        elif param.name == 'ioDocumentId' or param.name == 'inDocumentId':
            objId = self.topSolid.ts.Documents.GetDocument(docId)
            return objId 
        elif param.name == "inRecurses":
            return True  # Ou False, conforme necessário
        elif param.name == "inObjectIds" or param.name == "inObjectIds":            
            export_list = List[type(docId)]()  # Create a .NET compatible List of PdmObjectId
            export_list.Add(docId)  # Add your PdmObjectId to the .NET List            
            return export_list
        elif param.name == "inExportsForDelivery":
            return False
        elif param.name == "inExportsIncrementalPackage":
            return False
        elif param.name == "inFileFullPath":
            #get app root path
            root_path = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(root_path, self.topSolid.get_name(docId) + ".TopPkg")
        elif param.name == "inAsksUser":
            return False
        elif param.name == "inSaves":
            return True
        elif param.name == "inUpdatesAll":           
            return True
        elif param.name == "inExporterIx":
            return 10
        else:
            return None  # Adicione lógica para outros tipos de parâmetros conforme necessário

    def on_menu(self, event ):
        menu_id = event.GetId()
        attribute = self.menu_items.get(menu_id)
        if attribute and self.pdm:
            print(f"Selected attribute: {attribute}")
            command = getattr(self.pdm, attribute, None)
            if command:
                try:
                    # Verifica os argumentos do comando usando inspect
                    sig = inspect.signature(command)
                    # create a list to store the parameters
                    args = []
                    for param in sig.parameters.values():
                        # get the real value for the parameter
                        value = self.get_real_value_for_param(param, self.doc_id)
                        if value is not None:
                            args.append(value)
                    # execute the command
                    if command.__name__ == 'Update':
                        self.topSolid.ts.Application.StartModification("Update ", True)
                        doc = self.topSolid.ts.Documents.GetDocument(self.doc_id)
                        dirty_doc = self.topSolid.ts.Documents.EnsureIsDirty(doc)
                        #change doc id in args
                        args[0] = dirty_doc
                        result = command(*args)
                        self.topSolid.ts.Application.EndModification(True, True)

                    else:
                        result = command(*args)
                    print(f"Result: {self.topSolid.get_name(self.doc_id)} gets {command.__name__}")
                    if result:
                        wx.MessageBox(f"Result: {result}", "Success", wx.OK | wx.ICON_INFORMATION)

                except Exception as e:
                    print(f"Error executing {attribute}: {e}")
                    wx.MessageBox(f"Error executing {attribute}: {e}", "Error", wx.OK | wx.ICON_ERROR)
            else:
                print(f"Attribute {attribute} not found in pdm")
                wx.MessageBox(f"Attribute {attribute} not found in pdm", "Error", wx.OK | wx.ICON_ERROR)

    def ts_tree_menu(self, pdm_id):
        menu = wx.Menu()
        if pdm_id is str or pdm_id == "Folder":
            item_type_name = pdm_id
        else:

            doc = self.topSolid.ts.Documents.GetDocument(pdm_id)
            item_type_name = self.topSolid.get_type(doc)


        # Definir grupos de tipos
        pdm_group = [
            'TopSolid.Kernel.DB.Projects.ProjectDocument',
            'Folder'

        ]

        documents_group = [
            'TopSolid.Cad.Design.DB.Documents.PartDocument',
            'TopSolid.Cad.Design.DB.Documents.PartDocumentDesign',
            'TopSolid.Cam.NC.Kernel.DB.PartSetting.Documents.PartSettingDocument',
            'TopSolid.Cam.NC.MillTurn.DB.Documents.MillTurnDocument',
            'TopSolid.Cad.Drafting.DB.Documents.DraftingDocument'
        ]

        # Verificar o tipo e associar ao objeto correto
        if item_type_name in pdm_group:
            self.pdm = self.topSolid.ts.Pdm
        elif item_type_name in documents_group:
            self.pdm = self.topSolid.ts.Documents
        else:
            self.pdm = self.topSolid.ts.Pdm

        self.doc_id = pdm_id

        if self.pdm:
            for letter in "abcdefghijklmnopqrstuvwxyz":
                if any(attribute.lower().startswith(letter) for attribute in dir(self.pdm)):
                    submenu = wx.Menu()
                    for attribute in dir(self.pdm):
                        if attribute.lower().startswith(letter):
                            menu_item = submenu.Append(wx.ID_ANY, attribute)
                            self.menu_items[menu_item.GetId()] = attribute  # Armazena a associação entre o ID e o atributo
                            submenu.Bind(wx.EVT_MENU, self.on_menu, menu_item)
                    menu.AppendSubMenu(submenu, letter.upper())  # Add the submenu to the menu

        return menu


    def on_open(self, event):
        item = self.tree.GetSelection()
        if item:
            item_text = self.tree.GetItemText(item)
            print(item_text)
            #get all projects
            all_projects = self.topSolid.ts.Pdm.GetProjects(True, False)
            for project in all_projects:
                project_name = self.topSolid.get_name(project)
                if project_name == item_text:
                    print(project)
                    self.topSolid.ts.Pdm.OpenProject(project)
                    break
            constituents = self.topSolid.get_constituents(project)
            for constituent in constituents:
                constituent_name = self.topSolid.get_name(constituent)
                if constituent_name == item_text:
                    print(constituent)
                    #self.topSolid.ts.Pdm.OpenConstituent(constituent)
                    break
      
    def create_widgets(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        #add box to divise window in two vertical parts 
        self.gui_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.gui_sizer, 0, wx.ALL | wx.CENTER, 10)
        #make explorer sizer expandable au maximum
        explorer_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(explorer_sizer, 1, wx.ALL | wx.EXPAND, 10)
        #add two checkboxes to explorer sizer to select if we want to show all projects or only open projects, and to show all files or only project files
        check_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.show_all_projects = wx.CheckBox(self.panel, label="Show All Projects / Open projects", style=wx.ALIGN_CENTER)
        self.show_all_projects.Bind(wx.EVT_CHECKBOX, self.refresh_tree)
        check_sizer.Add(self.show_all_projects, 0, wx.ALL | wx.CENTER, 10)
        self.show_all_files = wx.CheckBox(self.panel, label="Only Project Files / Show All Files", style=wx.ALIGN_CENTER)
        self.show_all_files.Bind(wx.EVT_CHECKBOX, self.refresh_tree)
        check_sizer.Add(self.show_all_files, 0, wx.ALL | wx.CENTER, 10)
        explorer_sizer.Add(check_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        
        
        #add some treeview to show the projects and files and expandable au maximum
        self.tree = wx.TreeCtrl(self.panel, style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE)
        #make right click selected item and multiple selection
        self.tree.SetWindowStyleFlag(wx.TR_MULTIPLE | wx.ID_SELECTALL)
        self.tree.SetMinSize((200, 400))


        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_select)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_select) 
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_tree_right_click)
        
        explorer_sizer.Add(self.tree, 1, wx.ALL | wx.EXPAND, 10)
        

        
        # add one green circle to show if the connection is working or red if not
        self.connection_status = wx.StaticText(self.panel, label="Connection Status: Not Connected", style=wx.ALIGN_CENTER)
        self.gui_sizer.Add(self.connection_status, 0, wx.ALL | wx.CENTER, 10)
        # can add a listener to check if the connection is working and change the color of the circle
        if self.topSolid.connected:
            self.connection_status.SetLabel("Connection Status: Connected")
        else:
            self.connection_status.SetLabel("Connection Status: Not Connected")

        #get current project
        self.topSolid.get_current_project()
        if self.topSolid.current_proj_name:
            self.project_status = wx.StaticText(self.panel, label="Project Status: " + self.topSolid.current_proj_name, style=wx.ALIGN_CENTER)
            #bind to check if the project is changed
            self.project_status.Bind(wx.EVT_LEFT_DOWN, self.project_status_refresh)
        else:
            self.project_status = wx.StaticText(self.panel, label="Project Status: No Project Open", style=wx.ALIGN_CENTER)
        self.gui_sizer.Add(self.project_status, 0, wx.ALL | wx.CENTER, 10)

        #get open projects
        self.open_projects = self.topSolid.get_open_projects()
        if self.open_projects:
            self.open_projects_status = wx.StaticText(self.panel, label="Open Projects: " + str(len(self.open_projects)), style=wx.ALIGN_CENTER)
        else:
            self.open_projects_status = wx.StaticText(self.panel, label="Open Projects: No Open Projects", style=wx.ALIGN_CENTER)
        self.gui_sizer.Add(self.open_projects_status, 0, wx.ALL | wx.CENTER, 10)
        
        # Adiciona ComboBox para escolher a função
        functions = [
            '',
            "Test connection to TopSolid",
            "Get Current Project",
            "Get Constituents of Current Project",
            "Start Modification",
            "End Modification",
            "Open File",
            "Check In All Files",
            "Ask Plan",
            "Get Open Files",
            "Export all to pdfs",
            "Import File",
            "Import File w conversion",
            "Get tools",
            "Get elem constituents",
            "Get culture language",
            "Read functions from open file",
            "Export open projects TopPkg",
            "Export all projects TopPkg"
            
        ]

        self.function_combo = wx.ComboBox(self.panel, choices=functions, style=wx.CB_DROPDOWN)
        self.gui_sizer.Add(self.function_combo, 0, wx.ALL | wx.CENTER, 10)

        #create sizer for buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)

        btn_execute = wx.Button(self.panel, label="Execute")
        btn_execute.Bind(wx.EVT_BUTTON, self.on_execute)
        sizer_buttons.Add(btn_execute, 0, wx.ALL | wx.LEFT, 10)

        btn_add = wx.Button(self.panel, label="+ Adicionar Botão")
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_button)
        sizer_buttons.Add(btn_add, 0, wx.ALL | wx.CENTER, 10)

        self.gui_sizer.Add(sizer_buttons, 0, wx.ALL | wx.CENTER, 10)

        self.panel.SetSizer(sizer)

        self.load_buttons()
        
    def create_context_menu(self):
        menu = wx.Menu()
        item_remove = menu.Append(wx.ID_ANY, "Remove")
        self.Bind(wx.EVT_MENU, self.on_remove, item_remove)


        return menu
    
    def on_right_click(self, event):
        self.right_clicked_button = event.GetEventObject()
        self.PopupMenu(self.create_context_menu())

    def on_remove(self, event):

        # Use the stored reference to the button
        button = self.right_clicked_button

        # Remove the button from the saved buttons
        self.remove_button(button.GetLabel())

        # Remove the button
        if button:
            button.Destroy()
            self.panel.Layout()

  

    def remove_button(self, button_label):
        # Carrega os botões salvos
        saved_buttons = self.load_saved_buttons()

        # Remove o botão
        saved_buttons.remove(button_label)

        # Salva os botões
        with open('saved_buttons.json', 'w') as f:
            json.dump(saved_buttons, f)

    def on_add_button(self, event):
        selected_function = self.function_combo.GetValue()
        
        # add new button to panel with selected function
        new_button = wx.Button(self.panel, label=selected_function)
        new_button.Bind(wx.EVT_BUTTON, self.on_execute)
        new_button.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
 
        #self.panel.GetSizer().GetSizer().Add(new_button, 0, wx.ALL | wx.CENTER, 10)
        self.gui_sizer.Add(new_button, 0, wx.ALL | wx.CENTER, 10)
        self.panel.Layout()

        # Salva o botão adicionado
        self.save_button(selected_function)

    def save_button(self, button_label):
        # Carrega os botões salvos
        saved_buttons = self.load_saved_buttons()

        # Adiciona o novo botão
        saved_buttons.append(button_label)

        # Salva os botões
        with open('saved_buttons.json', 'w') as f:
            json.dump(saved_buttons, f)

    def load_buttons(self):
        # Carrega os botões salvos
        saved_buttons = self.load_saved_buttons()

        # Cria os botões
        for button_label in saved_buttons:
            button = wx.Button(self.panel, label=button_label)
            button.Bind(wx.EVT_BUTTON, self.on_execute) 
            button.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
            #self.panel.GetSizer().Add(button, 0, wx.ALL | wx.CENTER, 10)
            self.gui_sizer.Add(button, 0, wx.ALL | wx.CENTER, 10)

        self.panel.Layout()

    def load_saved_buttons(self):
        # Carrega os botões salvos
        try:
            with open('saved_buttons.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def on_execute(self, event):
        selected_function = event.GetEventObject().GetLabel()
        if selected_function == "":
            selected_function = self.function_combo.GetValue()
            

        if not self.topSolid or not self.topSolid.connected:
            self.topSolid = TopSolidAPI()

        with self.topSolid:
            if selected_function == "+ Adicionar Botão":
                self.on_add_button(event)
            elif selected_function == "Test connection to TopSolid":
                wx.MessageBox("Connected to TopSolid", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "Get Current Project":
                try:
                    self.topSolid.get_current_project()
                    name = self.topSolid.get_name(self.topSolid.current_project)
                    wx.MessageBox(f"Current Project: {name} - {self.topSolid.current_project}", "Success", wx.OK | wx.ICON_INFORMATION)
                except Exception as e:
                    wx.MessageBox("Error getting current project:", "Error", wx.OK | wx.ICON_ERROR)
                    
            elif selected_function == "Get Constituents of Current Project":
                lib_const = self.topSolid.get_constituents(None, True)
                wx.MessageBox(f"Constituents: {len(lib_const)}", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "Start Modification":
                self.topSolid.start_modif("op", "ot")
                wx.MessageBox("Start Modification", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "End Modification":
                self.topSolid.end_modif("op", "ot")
                wx.MessageBox("End Modification", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "Open File":
                # Adicione aqui a lógica para abrir um arquivo
                wx.MessageBox("File Opened", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "Check In All Files":
                self.topSolid.check_in_all(lib_const)
                wx.MessageBox("Checked In All Files", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "Ask Plan":
                # Adicione aqui a lógica para perguntar pelo plano
                wx.MessageBox("Asked Plan", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "Get Open Files":
                files = self.topSolid.get_open_files()
                wx.MessageBox(f"Open Files: {files}", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "Export all to pdfs":
                self.topSolid.get_current_project()
                name = self.topSolid.get_name(self.topSolid.current_project)
                print(name)
                lib_const = self.topSolid.get_constituents(None, True)
                print(lib_const)
                # get path to save pdfs
                dlg = wx.DirDialog(self, "Choose a folder to save pdfs", style=wx.DD_DEFAULT_STYLE)
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    print(path)
                dlg.Destroy()
                # add new folder with project name
                path = path + "\\" + name
                print(path)
                if not os.path.exists(path):
                    os.makedirs(path)
                self.topSolid.export_all_pdfs(path)


            elif selected_function == "Import File":
                self.topSolid.end_modif(True, False)
                # Adicione aqui a lógica para importar um arquivo
                dlg = wx.FileDialog(self, "Choose a file to import", wildcard="All files (*.*)|*.*", style=wx.FD_OPEN)
                if dlg.ShowModal() == wx.ID_OK:
                    file_path = dlg.GetPath()
                    dlg.Destroy()

                    # Lógica para obter o identificador do projeto ou pasta onde o arquivo será armazenado
                    # Neste exemplo, estou usando um identificador fictício (1) como proprietário.
                    owner_id = 1

                    # Lógica para obter o nome do novo documento
                    # Neste exemplo, estou usando o nome do arquivo como o nome do documento.
                    document_name = os.path.basename(file_path)


                    #lib, name = self.topSolid.get_current_project()
                    self.topSolid.get_current_project()

                try:
                    # Chama o método import_documents
                    imported_documents, log, bad_document_ids = self.topSolid.Import_file_w_conv(10, file_path, self.topSolid.current_project)
                    
                    # Examine os resultados conforme necessário
                    if imported_documents:
                        print(f"Documents imported successfully. Document IDs: {len(imported_documents)}", "Success", wx.OK | wx.ICON_INFORMATION)
                        for doc in imported_documents:
                            print(len(doc), doc)
                            for d in doc:
                                print(d)
                                self.topSolid.check_in(d)
                    else:
                        wx.MessageBox(f"Error importing documents. Log: {log}. Bad Document IDs: {bad_document_ids}", "Error", wx.OK | wx.ICON_ERROR)

                except Exception as e:
                    wx.MessageBox(f"Error importing documents: {e}", "Error", wx.OK | wx.ICON_ERROR)


            elif selected_function == "Import File w conversion":
                print("Import File w conversion")


            elif selected_function == "Get tools":
                doc = self.topSolid.get_open_files()
                print(doc)
                for d in doc:
                    print(d)
                    tools = self.topSolid.get_tools(d)
                    if tools:
                        print(tools)
                    else:
                        print("No tools")

            elif selected_function == "Get elem constituents":
                doc = self.topSolid.get_open_files()
                print(doc)
                f = open("output.txt", "w")
                for d in doc:
                    print(d)
                    #List<ElementId> GetElements(DocumentId inDocumentId)
                    elem = self.topSolid.ts.Elements.GetElements(d)
                    print(elem)
                    for e in elem:
                        consts = self.topSolid.ts.Elements.GetConstituents(e)
                        print("consts :: ", consts , len(consts))
                        for c in consts:
                            #print(self.topSolid.get_name(c), c.DocumentId , c.Id)
                            #output to txt file
                            f.write(self.topSolid.get_name(c) + " " + str(c.DocumentId) + " " + str(c.Id) + "\n")

                f.close()

            elif selected_function  == "Get culture language":
                print(self.topSolid.get_language())

            elif selected_function  == "Read functions from open file":
                doc = self.topSolid.get_open_files()
                print(doc)
                for d in doc:
                    print(d)
                    functions = self.topSolid.read_functions(d)
                    print(functions)

            elif selected_function == "Export open projects TopPkg":
                self.Export_project_pkg()
            elif selected_function == "Export all projects TopPkg":
                self.Export_all_project_pkg()


    def Export_all_project_pkg(self):
        all_proj = self.topSolid.ts.Pdm.GetProjects(True, False)
        #wxpython ask for folder to save
        dlg = wx.DirDialog(self, "Choose a folder to save TopPkg", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            root_path = dlg.GetPath()
            print(root_path)
        dlg.Destroy()
        counter = 0
        for i in all_proj:

            proj_name = self.topSolid.get_name(i)
            needsUpdating = self.topSolid.ts.Pdm.NeedsUpdating(i)
            print(proj_name, needsUpdating)
            #if needsUpdating:
            consts = self.topSolid.ts.Pdm.GetConstituents(i)
            for c in consts[1]:
                name = self.topSolid.get_name(c)
                needUp = self.topSolid.ts.Pdm.NeedsUpdating(c)
                if needUp:
                    print("needs updating")
                    doc = self.topSolid.ts.Documents.GetDocument(c)
                    # Uncomment the next line if you need to check out the document
                    # self.topSolid.ts.Documents.CheckOut(doc)
                    self.topSolid.ts.Application.StartModification("Update " + name, True)
                    ddoc = self.topSolid.ts.Documents.EnsureIsDirty(doc)
                    self.topSolid.ts.Documents.Refresh(ddoc)
                    self.topSolid.ts.Application.EndModification(True, True)
                    self.topSolid.ts.Documents.Save(ddoc)
            
            try:
                self.topSolid.ts.Pdm.CheckIn(i, True)

                export_list = List[type(i)]()  # Create a .NET compatible List of PdmObjectId
                export_list.Add(i)  # Add your PdmObjectId to the .NET List
                path = root_path + "\\" + proj_name + ".TopPkg"
                print(path)
                self.topSolid.ts.Pdm.ExportPackage(export_list, False, False, path )
            except Exception as e:
                print(f"Error exporting project {proj_name}: {e}")

            counter += 1  # Increment the counter inside the loop


    def Export_project_pkg(self):
        self.topSolid.get_current_project()
        name = self.topSolid.get_name(self.topSolid.current_project)
        print(name)

        open_projects = self.topSolid.ts.Pdm.GetOpenProjects(True, True)
        print(len(open_projects))

        counter = 0
        for i in open_projects:
            proj_name = self.topSolid.get_name(i)
            needsUpdating = self.topSolid.ts.Pdm.NeedsUpdating(i)
            print(proj_name, needsUpdating)
            #if needsUpdating:
            consts = self.topSolid.ts.Pdm.GetConstituents(i)
            for c in consts[1]:
                name = self.topSolid.get_name(c)
                needUp = self.topSolid.ts.Pdm.NeedsUpdating(c)
                if needUp:
                    print("needs updating")
                    doc = self.topSolid.ts.Documents.GetDocument(c)
                    # Uncomment the next line if you need to check out the document
                    # self.topSolid.ts.Documents.CheckOut(doc)
                    self.topSolid.ts.Application.StartModification("Update " + name, True)
                    ddoc = self.topSolid.ts.Documents.EnsureIsDirty(doc)
                    self.topSolid.ts.Documents.Refresh(ddoc)
                    self.topSolid.ts.Application.EndModification(True, True)
                    self.topSolid.ts.Documents.Save(ddoc)
            #else:
            try:
                self.topSolid.ts.Pdm.CheckIn(i, True)

                export_list = List[type(i)]()  # Create a .NET compatible List of PdmObjectId
                export_list.Add(i)  # Add your PdmObjectId to the .NET List
                self.topSolid.ts.Pdm.ExportPackage(export_list, False, False, "C:\\users\\user\\desktop\\" + proj_name + ".TopPkg")
            except Exception as e:
                print(e)
                
            counter += 1  # Increment the counter inside the loop

    def on_add_buttonç(self, event):
        selected_function = self.function_combo.GetValue()
        
        # add new button to panel with selected function
        new_button = wx.Button(self.panel, label=selected_function)
        new_button.Bind(wx.EVT_BUTTON, self.on_execute) 
        self.panel.GetSizer().Add(new_button, 0, wx.ALL | wx.CENTER, 10)
        self.panel.Layout()

    def on_close(self, event):
        self.Destroy()

def main():
    app = wx.App(False)
    frame = TopSolidGUI(None, "TopSolid Script GUI")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
