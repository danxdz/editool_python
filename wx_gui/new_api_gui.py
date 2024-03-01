import wx
import os

# Import the TopSolidAPI class from the top_solid_api module
from topsolid_api import TopSolidAPI



class TopSolidGUI(wx.Frame):
    def __init__(self, parent, title):
        super(TopSolidGUI, self).__init__(parent, title=title, size=(400, 300))

        self.topSolid = None  # Manter uma instância da classe TopSolidAPI
        self.panel = wx.Panel(self)
        self.create_widgets()
        self.Bind(wx.EVT_CLOSE, self.on_close)

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
                lib, name = self.topSolid.get_current_project()
                wx.MessageBox(f"Current Project: {name}", "Success", wx.OK | wx.ICON_INFORMATION)
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
                lib, name = self.topSolid.get_current_project()
                print(lib, name)
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


                    lib, name = self.topSolid.get_current_project()

                try:
                    # Chama o método import_documents
                    imported_documents, log, bad_document_ids = self.topSolid.Import_file_w_conv(10, file_path, lib)
                    
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


    def on_add_button(self, event):
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
