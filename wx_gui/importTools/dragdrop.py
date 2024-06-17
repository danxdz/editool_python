import wx 
import logging

from importTools import import_xml_wx

from importTools.validateImportDialogue import validateToolDialog

from gui.guiTools import FileDialogHandler

class FileDrop(wx.FileDropTarget):
    def __init__(self, parent, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.supported_extensions = ['stp', 'step', 'xml']

        self.parent = parent

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            logging.info("Dropped file: %s" % filename)
            # Get the file extension
            file_extension = filename.split('.')[-1].lower()
            if file_extension in self.supported_extensions:
                self.OnDropFile(filename, filename.split('\\')[-1].split('.')[0].lower(), file_extension)
            else:
                logging.error("File type not supported: %s" % file_extension)
                wx.MessageBox("File type not supported: %s" % file_extension, "Error", wx.OK | wx.ICON_ERROR)
        return True
    
    def OnDropFile(self, path,  filename, file_extension):
    # Call the function to handle the file import
        
        # Handle the dropped file here
        print("Dropped file:", filename, "Extension:", file_extension)
        # call xml import
        if file_extension == 'xml':
            print("xml file")
            tools = import_xml_wx.import_xml_file(self, path)
            self.on_new_tool(tools)            

        # call step import
        elif file_extension in ['stp', 'step']:
            print("step file")
            self.on_import_step(None, path)

    
    def on_new_tool(self, tools):


        for tool in tools:
            validateToolDialog(self.parent, tool, True).ShowModal()

   

    def on_import_step(self, event, file_path=None):
        '''import a step file and convert it to a tool'''
        
        if not file_path:
            title = "Choose a STEP file to import"
            wcard = "Step files (*.stp, *.step)|*.stp;*.step"
            file_path = FileDialogHandler.open_file_dialog(self, title, wcard)
        
        else:
            try:
            
                self.ts = self.window.ts
                self.ts.get_current_project()
                msg = f"Error importing documents: "

                imported_documents, log, bad_document_ids = self.ts.Import_file_w_conv(10, file_path, self.ts.current_project)
                
                if imported_documents:
                    print(f"Documents imported successfully. Document IDs: {len(imported_documents)}", "Success", wx.OK | wx.ICON_INFORMATION)
                    for doc in imported_documents:
                        print(len(doc), doc)
                        for d in doc:
                            print(d)
                            self.ts.check_in(d)
                else:
                    wx.MessageBox(f"{msg} Log: {log}. Bad Document IDs: {bad_document_ids}", "Error", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                wx.MessageBox(f"{msg} {e}", "Error", wx.OK | wx.ICON_ERROR)
                logging.error(msg)