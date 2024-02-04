import wx
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
            "Export all to pdfs"
        ]

        self.function_combo = wx.ComboBox(self.panel, choices=functions, style=wx.CB_DROPDOWN)
        sizer.Add(self.function_combo, 0, wx.ALL | wx.CENTER, 10)

        btn_execute = wx.Button(self.panel, label="Execute")
        btn_execute.Bind(wx.EVT_BUTTON, self.on_execute)
        sizer.Add(btn_execute, 0, wx.ALL | wx.CENTER, 10)

        self.panel.SetSizer(sizer)

    def on_execute(self, event):
        selected_function = self.function_combo.GetValue()

        if not self.topSolid or not self.topSolid.connected:
            self.topSolid = TopSolidAPI()

        with self.topSolid:
            if selected_function == "Test connection to TopSolid":
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

                #get path to save pdfs
                dlg = wx.DirDialog(self, "Choose a folder to save pdfs", style=wx.DD_DEFAULT_STYLE)
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    print(path)
                dlg.Destroy()

                #add new folder with project name
                path = path + "\\" + name
                print(path)
                import os
                if not os.path.exists(path):
                    os.makedirs(path)

                self.topSolid.export_all_pdfs(path)  




    def on_close(self, event):
        self.Destroy()

def main():
    app = wx.App(False)
    frame = TopSolidGUI(None, "TopSolid Script GUI")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
