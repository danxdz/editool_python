import wx
import wx.html2
import os
import sys

class HelpFrame(wx.Frame):
    def __init__(self, parent, title, lang):
        super(HelpFrame, self).__init__(parent, title=title, size=(600, 400))

        self.panel = wx.Panel(self)
        self.browser = wx.html2.WebView.New(self.panel)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.panel.SetSizer(self.sizer)
        
        path = self.get_html_file_path(lang)

        self.load_help_file(path)

        self.CreateStatusBar()
        self.Centre()
        self.Show()

    def get_html_file_path(self,lang):
        # get the directory where the python file is located
        exe_dir = os.path.dirname(sys.argv[0])
        # make the help file path
        print(exe_dir)
        html_file_path = os.path.join(exe_dir, "help/help_" + lang + ".html")
        return html_file_path

    def load_help_file(self, filename):
        # Carregar o conteúdo do arquivo HTML de ajuda
        try:
            with open(filename, "r", encoding="utf-8") as f:
                html_content = f.read()
                self.browser.SetPage(html_content, "")
        except IOError:
            wx.LogError("O arquivo de ajuda não pôde ser encontrado.")

