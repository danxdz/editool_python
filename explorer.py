import os
import wx

class FileExplorer(wx.Frame):
    def __init__(self, parent, title):
        super(FileExplorer, self).__init__(parent, title=title, size=(800, 400))
        self.panel = wx.Panel(self)
        self.textbox = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.list = wx.ListCtrl(self.panel, style=wx.LC_REPORT)
        self.config = wx.Config("FileExplorer")
        self.root_path = self.config.Read("root_path", "")

        self.search_text = ""

        # Adicione uma coluna invisível com largura zero
        self.list.InsertColumn(0, 'Name')
        self.list.InsertColumn(1, 'Has .step', format=wx.LIST_FORMAT_RIGHT, width=100)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.textbox, 0, wx.EXPAND)
        self.sizer.Add(self.list, 1, wx.EXPAND)

        self.panel.SetSizer(self.sizer)

        self.textbox.Bind(wx.EVT_TEXT, self.on_text_changed)
        #self.root_path = ""
        if not self.root_path or not os.path.exists(self.root_path):
            self.get_initial_path()

        self.populate_list(self.root_path)
        self.Show()

    def get_initial_path(self):
        dialog = wx.DirDialog(None, "Select the initial directory:")
        if dialog.ShowModal() == wx.ID_OK:
            self.root_path = dialog.GetPath()
            self.config.Write("root_path", self.root_path)
        dialog.Destroy()

    def on_text_changed(self, event):
        self.search_text = self.textbox.GetValue().lower()
        self.list.DeleteAllItems()
        self.populate_list(self.root_path)

    def populate_list(self, path):
        for root, dirs, files in os.walk(path):
            for item in dirs:
                full_path = os.path.join(root, item)
                has_step_file = any(f.lower().endswith('.step') or f.lower().endswith('.stp') or f.lower().endswith('.iges') or f.lower().endswith('.igs') for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f)))
                if self.search_text == "" or self.search_text in item.lower():
                    index = self.list.InsertItem(self.list.GetItemCount(), item)
                    self.list.CheckItem(index, has_step_file)
                    self.list.SetItem(index, 1, "Yes" if has_step_file else "No")

if __name__ == '__main__':
    app = wx.App()
    FileExplorer(None, "File Explorer")
    app.MainLoop()
