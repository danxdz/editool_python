import logging
import wx
import os
import json

# Import the TopSolidAPI class from the top_solid_api module
from topsolid_api import TopSolidAPI



class TopSolidGUI(wx.Frame):
    def __init__(self, parent, title):
        super(TopSolidGUI, self).__init__(parent, title=title, size=(400, 300))

        self.topSolid = None  # Manter uma instância da classe TopSolidAPI
        self.panel = wx.Panel(self)
        self.create_widgets()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.right_clicked_button = None 


    def create_widgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Adiciona ComboBox para escolher a função
        functions = [
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
            
        ]

        self.function_combo = wx.ComboBox(self.panel, choices=functions, style=wx.CB_DROPDOWN)
        sizer.Add(self.function_combo, 0, wx.ALL | wx.CENTER, 10)

        btn_execute = wx.Button(self.panel, label="Execute")
        btn_execute.Bind(wx.EVT_BUTTON, self.on_execute)
        sizer.Add(btn_execute, 0, wx.ALL | wx.CENTER, 10)

        btn_add = wx.Button(self.panel, label="+ Adicionar Botão")
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_button)
        sizer.Add(btn_add, 0, wx.ALL | wx.CENTER, 10)

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
 
        self.panel.GetSizer().Add(new_button, 0, wx.ALL | wx.CENTER, 10)
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
            self.panel.GetSizer().Add(button, 0, wx.ALL | wx.CENTER, 10)

        self.panel.Layout()

    def load_saved_buttons(self):
        # Carrega os botões salvos
        try:
            with open('saved_buttons.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def on_execute(self, event):
        selected_function = self.function_combo.GetValue()

        if not self.topSolid or not self.topSolid.connected:
            self.topSolid = TopSolidAPI()

        with self.topSolid:
            if selected_function == "+ Adicionar Botão":
                self.on_add_button(event)
            elif selected_function == "Test connection to TopSolid":
                wx.MessageBox("Connected to TopSolid", "Success", wx.OK | wx.ICON_INFORMATION)
            elif selected_function == "Get Current Project":
                self.topSolid.get_current_project()
                name = self.topSolid.get_name(self.topSolid.current_project)
                wx.MessageBox(f"Current Project: {name} - {self.topSolid.current_project}", "Success", wx.OK | wx.ICON_INFORMATION)
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
                    print(tools)

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
