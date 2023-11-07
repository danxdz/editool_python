import os
import wx

class FileExplorer(wx.Frame):
    def __init__(self, parent, title):
        super(FileExplorer, self).__init__(parent, title=title, size=(600, 400))
        self.panel = wx.Panel(self)
        self.textbox = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.tree = wx.TreeCtrl(self.panel)
        self.config = wx.Config("FileExplorer")
        self.root_path = self.config.Read("root_path", "")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.textbox, 0, wx.EXPAND)
        self.sizer.Add(self.tree, 1, wx.EXPAND)

        self.panel.SetSizer(self.sizer)

        self.textbox.Bind(wx.EVT_TEXT, self.on_text_changed)

        if not self.root_path or not os.path.exists(self.root_path):
            self.get_initial_path()

        self.root = self.tree.AddRoot(self.root_path)
        
        self.Show()

    def get_initial_path(self):
        dialog = wx.DirDialog(None, "Select the initial directory:")
        if dialog.ShowModal() == wx.ID_OK:
            self.root_path = dialog.GetPath()
            self.config.Write("root_path", self.root_path)
        dialog.Destroy()

    def on_text_changed(self, event):
        search_text = self.textbox.GetValue().lower()
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot(self.root_path)
        self.tree.Expand(self.root)
        self.populate_tree(self.root, self.root_path, search_text)



    def get_item_path(self, item):
        path = self.tree.GetItemText(item)
        parent = self.tree.GetItemParent(item)
        while parent.IsOk():
            path = os.path.join(self.tree.GetItemText(parent), path)
            parent = self.tree.GetItemParent(parent)
        return path

    def populate_tree(self, parent, path, search_text=""):
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path) and (search_text == "" or search_text in item.lower()):
                child = self.tree.AppendItem(parent, item)
                self.tree.SetItemImage(child, 0, wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(child, 0, wx.TreeItemIcon_Expanded)
                self.tree.SetItemHasChildren(child)
            elif not os.path.isdir(full_path) and (search_text == "" or search_text in item.lower()):
                self.tree.AppendItem(parent, item)
        self.tree.ExpandAll()

if __name__ == '__main__':
    app = wx.App()
    FileExplorer(None, "File Explorer")
    app.MainLoop()
