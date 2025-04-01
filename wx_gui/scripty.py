import os
import inspect
import tkinter as tk
from tkinter import Menu, filedialog, messagebox, scrolledtext
from topsolid_api import TopSolidAPI

import clr
clr.AddReference("System")
from System.Collections.Generic import List 


class TopSolidGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TopSolid Script Editor")
        self.geometry("800x600")
        self.topSolid = TopSolidAPI()
        self.menu_items = {}
        self.doc_id = None  # Add doc_id initialization

        self.InitUI()

    def InitUI(self):
        self.script_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.script_area.pack(expand=True, fill=tk.BOTH)

        self.script_area.bind("<Button-3>", self.OnRightClick)

        self.CreateMenuBar()

        # Create an execute button
        self.execute_button = tk.Button(self, text="Execute", command=self.OnExecute)
        self.execute_button.pack()

    def OnExecute(self):
        script = self.script_area.get("1.0", tk.END).strip()
        lines = script.split('\n')
        
        for line in lines:
            result = self.execute_line(line)
            if result is not None:
                messagebox.showinfo("Success", f"Result: {result}")

    def execute_line(self, line):
        try:
            method_name, args = self.parse_line(line)
            obj = self.get_method_object(method_name)
            real_args = self.get_real_arguments(obj, args)
            return self.invoke_method(obj, real_args)
        except Exception as e:
            print(f"Error executing {method_name}: {e}")
            messagebox.showerror("Error", f"Error executing {method_name}: {e}")
            return None

    def parse_line(self, line):
        method_name = line.split('(')[0]
        args_str = line.split('(')[1].rstrip(')')
        args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
        return method_name, args

    def get_method_object(self, method_name):
        obj = self.topSolid.ts
        for part in method_name.split('.'):
            obj = getattr(obj, part)
        return obj

    def get_real_arguments(self, obj, args):
        passed_args = []
        for arg in args:
            if '.' in arg:
                arg_obj = self.get_method_object(arg)
                if callable(arg_obj):
                    passed_args.append(arg_obj())
        return self.resolve_arguments(obj, passed_args)

    def resolve_arguments(self, obj, passed_args):
        sig = inspect.signature(obj)
        real_args = []
        for param in sig.parameters.values():
            if passed_args:
                for arg in passed_args:
                    if param.name == "inObjectIds":
                        self.doc_id = arg[0]
                        real_args.append(arg)
                    else:
                        real_args.append(self.get_real_value_for_param(param, self.doc_id))
            else:
                value = self.get_real_value_for_param(param, self.doc_id)
                if value is not None:
                    real_args.append(value)
        return real_args

    def invoke_method(self, obj, args):
        if obj.__name__ == 'Update':
            self.topSolid.ts.Application.StartModification("Update", True)
            doc = self.topSolid.ts.Documents.GetDocument(self.doc_id)
            dirty_doc = self.topSolid.ts.Documents.EnsureIsDirty(doc)
            args[0] = dirty_doc
            result = obj(*args)
            self.topSolid.ts.Application.EndModification(True, True)
        else:
            result = obj(*args)
        print(f"Result: {self.topSolid.get_name(self.doc_id)} gets {obj.__name__}")
        return result

    def CreateMenuBar(self):
        menubar = Menu(self)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Script", command=self.OnSaveScript)
        file_menu.add_command(label="Load Script", command=self.OnLoadScript)
        menubar.add_cascade(label="File", menu=file_menu)

        self.config(menu=menubar)

    def CreateSubMenu(self, api_object, menu_name):
        submenu = Menu(self.context_menu, tearoff=0)
        for letter in "abcdefghijklmnopqrstuvwxyz":
            if any(attribute.lower().startswith(letter) for attribute in dir(api_object) if not attribute.startswith('_')):
                letter_menu = Menu(submenu, tearoff=0)
                for attribute in dir(api_object):
                    if attribute.lower().startswith(letter) and not attribute.startswith('_'):
                        letter_menu.add_command(label=attribute, command=lambda attr=f"{menu_name}.{attribute}": self.OnAPIMethodSelected(attr))
                        if not callable(getattr(api_object, attribute)):
                            sub_submenu = Menu(letter_menu, tearoff=0)
                            for sub_attribute in dir(getattr(api_object, attribute)):
                                if not sub_attribute.startswith('_'):
                                    sub_submenu.add_command(label=sub_attribute, command=lambda attr=f"{menu_name}.{attribute}.{sub_attribute}": self.OnAPIMethodSelected(attr))
                            letter_menu.add_cascade(label=attribute, menu=sub_submenu)
                submenu.add_cascade(label=letter.upper(), menu=letter_menu)
        return submenu

    def OnRightClick(self, event):
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.OnCut)
        self.context_menu.add_command(label="Copy", command=self.OnCopy)
        self.context_menu.add_command(label="Paste", command=self.OnPaste)

        pdm_menu = self.CreateSubMenu(self.topSolid.ts.Pdm, "Pdm")
        doc_menu = self.CreateSubMenu(self.topSolid.ts.Documents, "Documents")
        api_methods_menu = self.CreateSubMenu(self.topSolid.ts, "General")

        self.context_menu.add_cascade(label="API Methods", menu=api_methods_menu)
        self.context_menu.add_cascade(label="Pdm", menu=pdm_menu)
        self.context_menu.add_cascade(label="Documents", menu=doc_menu)

        self.context_menu.tk_popup(event.x_root, event.y_root)

    def OnAPIMethodSelected(self, method_name):
        self.script_area.insert(tk.END, f"{method_name}()\n")

    def OnSaveScript(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.script_area.get("1.0", tk.END))
            except IOError:
                messagebox.showerror("Error", f"Cannot save current data in file '{file_path}'.")

    def OnLoadScript(self):
        file_path = filedialog.askopenfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.script_area.delete("1.0", tk.END)
                    self.script_area.insert(tk.END, file.read())
            except IOError:
                messagebox.showerror("Error", f"Cannot open file '{file_path}'.")

    def OnCut(self):
        self.script_area.event_generate("<<Cut>>")

    def OnCopy(self):
        self.script_area.event_generate("<<Copy>>")

    def OnPaste(self):
        self.script_area.event_generate("<<Paste>>")
    
    def make_path(self, path):
        try:
            res = os.makedirs(path, exist_ok=True)
            print("MAKE_PATH :: dir created :: ", path, res)
        except Exception as ex:
            print("error :: ", ex)
            pass

    def get_real_value_for_param(self, param, docId=None):
        if param.name in ['inObjectId', 'inProjectId', 'inProjectFolderId']:
            return docId        
        elif param.name in ['ioDocumentId', 'inDocumentId']:
            if docId is None:
                current_project = self.topSolid.ts.Pdm.GetCurrentProject()
                proj_const = self.topSolid.ts.Pdm.GetConstituents(current_project)

                for const in proj_const:
                    for elem in const:
                        elem_type = self.topSolid.get_type(elem)

                        if elem_type == ".TopDft":
                            doc_id = self.topSolid.ts.Documents.GetDocument(elem)
                            doc_name = self.topSolid.ts.Documents.GetName(doc_id)

                            export_path_docs = os.path.join(self.ts.Application.GetPath(1), "ExportedDocs")

                            self.make_path(export_path_docs)

                            exporter_type = self.topSolid.ts.Application.GetExporterFileType(10, "outFile", "outExt")
                            complete_path = os.path.join(export_path_docs, f"{doc_name}{exporter_type[1][0]}")

                            export = self.topSolid.ts.Documents.Export(10, doc_id, complete_path)
                            objId = self.topSolid.ts.Documents.GetDocument(doc_id)

            else:
                objId = self.topSolid.ts.Documents.GetDocument(docId)
            return objId 
        elif param.name == "inRecurses":
            return True
        elif param.name == "inObjectIds":
            if docId is None:
                return None          
            export_list = List[type(docId)]()
            export_list.Add(docId)
            return export_list
        elif param.name == "inExportsForDelivery":
            return False
        elif param.name == "inExportsIncrementalPackage":
            return False
        elif param.name == "inFileFullPath":
            root_path = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(root_path, self.topSolid.get_name(docId), ".TopPkg")
        elif param.name == "inAsksUser":
            return False
        elif param.name == "inSaves":
            return True
        elif param.name == "inUpdatesAll":           
            return True
        elif param.name == "inExporterIx":
            return 10
        elif param.name == "inOptions":
            return None
        else:
            return None

if __name__ == '__main__':
    app = TopSolidGUI()
    app.mainloop()
