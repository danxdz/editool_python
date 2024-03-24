import wx 
import logging

class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.supported_extensions = ['stp', 'step', 'xml']

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            logging.info("Dropped file: %s" % filename)
            # Get the file extension
            file_extension = filename.split('.')[-1].lower()
            if file_extension in self.supported_extensions:
                self.window.OnDropFile(filename, filename.split('\\')[-1].split('.')[0].lower(), file_extension)
            else:
                logging.error("File type not supported: %s" % file_extension)
                wx.MessageBox("File type not supported: %s" % file_extension, "Error", wx.OK | wx.ICON_ERROR)
        return True