import winreg
import os
import clr

import wx

class TopSolidAPI:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect_topsolid()

    def __init__(self):
        self.design = None
        self.connected = False
        self._initialize_topsolid()

    def _initialize_topsolid(self):
        key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

        try:
            sub_keys = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            sub_keys_count = winreg.QueryInfoKey(sub_keys)[0]
            top_solid_version = winreg.EnumKey(sub_keys, sub_keys_count - 1)
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path + "\\" + top_solid_version, 0, winreg.KEY_READ)
            value = winreg.QueryValueEx(key, "InstallDir")

            top_solid_path = value[0]

            top_solid_kernel_sx_path = os.path.join(top_solid_path, "bin", "TopSolid.Kernel.SX.dll")
            print(f"Loading dll: {top_solid_kernel_sx_path}")
            clr.AddReference(top_solid_kernel_sx_path)

            top_solid_kernel_path = os.path.join(top_solid_path, "bin", "TopSolid.Kernel.Automating.dll")
            print(f"Loading dll: {top_solid_kernel_path}")
            clr.AddReference(top_solid_kernel_path)

            clr.setPreload(True)

            import TopSolid.Kernel.Automating as Automating
            
            from TopSolid.Kernel.Automating import PdmObjectId
            from TopSolid.Kernel.Automating import DocumentId
            from TopSolid.Kernel.Automating import ElementId
            from TopSolid.Kernel.Automating import SmartText

            top_solid_kernel_type = Automating.TopSolidHostInstance
            self.design = clr.System.Activator.CreateInstance(top_solid_kernel_type)

            # Connect to TopSolid
            self.design.Connect()

            

            print("TopSolid " + top_solid_version + " connected successfully!")
            self.connected = True 

        except Exception as ex:
            print("Error initializing TopSolid:", ex)
            self.connected = False

    def disconnect_topsolid(self):
        try:
            if self.design is not None:
                self.design.Disconnect()
                print("Disconnected from TopSolid")
                self.connected = False
        except Exception as ex:
            print("Error disconnecting from TopSolid:", ex)
            self.connected = False

    def get_default_tools_lib(self):
        # Load TopSolid DLLs
        if self.design is None:
            # Handle error
            return None

        PdmObjectIdType = type(self.design.Pdm.SearchProjectByName("TopSolid Machining User Tools")) #cheat to get type
        PdmObjectIdType = self.design.Pdm.SearchProjectByName("TopSolid Machining User Tools")


        for i in PdmObjectIdType:
            name = self.design.Pdm.GetName(i)
            #print("name: ", name)
            if name == "Outils d'usinage utilisateur TopSolid" or name == "TopSolid Machining User Tools":
                PdmObjectIdType.Clear()
                PdmObjectIdType.Add(i)
                break

        return PdmObjectIdType, name
    

    def start_modif(self, op, ot):
        try:
            self.design.Application.StartModification(op, ot)
            print("Start modifications")
        except Exception as ex:
            print(str(ex))
        finally:
            print("Modifications started")

    def end_modif(self, op, ot):
        try:
            self.design.Application.EndModification(op, ot)
            print("End modifications")
        except Exception as ex:
            print(str(ex))
        finally:
            print("All modifications ended")


    def init_folders(self):
        try:
            # Get Topsolid types
            current_project = self.design.Pdm.GetCurrentProject()
            current_proj_name = self.get_name(current_project)

            proj_const = self.design.Pdm.GetConstituents(current_project)
            print(f"{str(len(proj_const[0]) - 1)} folders in root project, {str(len(proj_const[1]))} files in root project")

            consts = self.check_folder_or_file(proj_const)
            print("consts :: ", consts)

            return consts

        except Exception as ex:
            # Handle
            print("error :: ", ex)

    def get_constituents(self, proj, printInfo = False):
        '''get constituents of current project'''
        if proj is None:
            proj = self.design.Pdm.GetCurrentProject()

        proj_const = self.design.Pdm.GetConstituents(proj)
        proj_name = self.get_name(proj)
 
        files = self.check_folder_or_file(proj_const, printInfo)
        
        if printInfo:
            self.print_folder(proj_const, proj_name)

        return files

    def check_folder_or_file(self, folder_const, printInfo = False):
        
        files = []

        for file in folder_const[1]:
            #printInfo(file, "files")
            self.filter_types(file, printInfo)
            files.append(file)
            
        for dir in folder_const[0]:
            print ("folder path ::", self.get_name(dir))

            iFiles = self.get_constituents(dir, printInfo)
            for i in iFiles:
                files.append(i)

        return files


    def filter_types(self, file, printInfo = False):
        file_type = self.get_type(file)
        match file_type:
            case ".TopPrt":
                type_text = "part"               
            case ".TopAsm":
                type_text = "assembly"
            case ".TopDft":
                type_text = "drawing"
            case ".TopMillTurn":
                type_text = "mill turn"
            case ".TopMacComp":
                type_text = "machine component"
            case ".png":
                type_text = "image"
            case ".jpg":
                type_text = "image"
            case ".pdf":
                type_text = "pdf"
            case ".doc":
                type_text = "word"
            case ".docx":
                type_text = "word"
            case ".xls":
                type_text = "excel"
            case ".xlsx":
                type_text = "excel"
            case ".nc":
                type_text = "nc"
            case ".iso":
                type_text = "iso"
            case ".h":
                type_text = "heidenhain"
            case ".mpf":
                type_text = "siemens SINUMERIK"
            case ".stp":
                type_text = "step"

            case _:
                type_text = "unknown file type"
        
        if printInfo:
            print(f"{self.get_name(file)} : {file_type} :: {type_text}")

    def get_type(self, obj):
        obj_type = type(obj)
        ts_type = ""

    
        from TopSolid.Kernel.Automating import PdmObjectId
        from TopSolid.Kernel.Automating import DocumentId
        from TopSolid.Kernel.Automating import ElementId

        if obj_type is PdmObjectId:
            raw_ts_type = self.design.Pdm.GetType(obj)
            if str(raw_ts_type[0]) == "Folder":
                ts_type = str(raw_ts_type[0])
            else:
                ts_type = str(self.design.Pdm.GetType(obj)[1])
        elif obj_type is DocumentId:
            is_part = self.design.Documents.IsPart(obj)
            ts_type = str(self.design.Documents.GetType(obj)[0])
        elif obj_type is ElementId:
            ts_type = str(self.design.Elements.GetTypeFullName(obj))

        return ts_type

    def get_name(self, obj):
        '''get name of object by type, either PdmObjectId, DocumentId or ElementId'''
        obj_type = type(obj)
        name = ""
    
        from TopSolid.Kernel.Automating import PdmObjectId
        from TopSolid.Kernel.Automating import DocumentId
        from TopSolid.Kernel.Automating import ElementId

        if obj_type is PdmObjectId:
            name = str(self.design.Pdm.GetName(obj))
        elif obj_type is DocumentId:
            name = str(self.design.Documents.GetName(obj))
        elif obj_type is ElementId:
            name = str(self.design.Elements.GetName(obj))

        return name

    def print_info(self, file, msg):
        '''print info about TS object'''
        file_name = self.get_name(file)
        file_type = self.get_type(file)
        print(msg, " ; ", file_name, " ; ", file_type)

    def print_folder(self, folder_const, folder_name):
        if len(folder_const[0]) > 0 or len(folder_const[1]) > 0:
            print(f"project {folder_name} @ have ", end="")
            if len(folder_const[0]) > 0:
                print(f"{len(folder_const[0])} folders ", end="")
            if len(folder_const[1]) > 0:
                print(f"{len(folder_const[1])} files")
            else:
                print("")
        else:
            print(f"dir {folder_name} is empty")

    def get_current_project(self):
        current_project = self.design.Pdm.GetCurrentProject()
        #get current project name
        current_proj_name = self.get_name(current_project)
        return current_project, current_proj_name
    

    def open_file(self, file):
        '''open file in TopSolid'''
        try:
            #docId = self.ts_ext.Documents.GetDocument(file)
            self.design.Documents.Open(file)
            print("file opened")
        except Exception as ex:
            print(str(ex))
        finally:
            print("All modifications ended")

    def check_in_all(self, files):
        '''check in all files in list'''
        from TopSolid.Kernel.Automating import PdmObjectId
        #need a list of PdmObjectId
        for file in files:
            self.design.Pdm.CheckIn(file, True)


    def ask_plan(self, file):

        from TopSolid.Kernel.Automating import UserQuestion

       

        '''ask repere of file'''
        try:
           
            titre = "Plan XY"
            label = "Merci de sélectionner le plan XY du repère"
            QuestionPlan = UserQuestion(titre, label)
            QuestionPlan.AllowsCreation = True

            ReponseRepereUser = None            
            ReponseRepereUser = self.design.User.AskFrame3D(QuestionPlan, True, None, ReponseRepereUser)
            print(ReponseRepereUser)
            if ReponseRepereUser[1]:
                print("plan selected")
                frame = ReponseRepereUser[1]
                print(frame)
                frame_elem_id = frame.ElementId
                print(frame_elem_id)
                frame_name = self.get_name(frame_elem_id)
                print(frame_name)

        except Exception as ex:
            print(str(ex))
        finally:
            print("All modifications ended")

    def get_open_files(self, file_type = None):
        '''get open files'''
        try:
            docId = []
            tmp = self.design.Documents.GetOpenDocuments()
            num = len(tmp)
            print(f"number of open files : {num}")
            if tmp is not None:
                if tmp.Count > 1:
                    for i in tmp:
                        docId.append(i)
                    return docId
                else:
                    return tmp
            
            print(f"file opened : {docId}")
            return docId
        except Exception as ex:
            print(str(ex))
        finally:
            print("All modifications ended")




    def make_path(self, path):
        try:
            res = os.makedirs(path, exist_ok=True)
            print("MAKE_PATH :: dir created :: ", path, res)
        except Exception as ex:
            # Handle
            print("error :: ", ex)
            pass


    def export_all_pdfs(self, export_path_docs):
        current_project = self.design.Pdm.GetCurrentProject()
        proj_const = self.design.Pdm.GetConstituents(current_project)

        for const in proj_const:
            for elem in const:
                elem_name = self.design.Pdm.GetName(elem)
                elem_type = self.get_type(elem)

                if elem_type == ".TopDft":
                    doc_id = self.design.Documents.GetDocument(elem)
                    doc_name = self.design.Documents.GetName(doc_id)

                    self.make_path(export_path_docs)

                    exporter_type = self.design.Application.GetExporterFileType(10, "outFile", "outExt")  # 10 for pdf
                    complete_path = os.path.join(export_path_docs, f"{doc_name}{exporter_type[1][0]}")

                    export = self.design.Documents.Export(10, doc_id, complete_path)  # 10 for pdf



    '''********************                     file explorer functions'''

    def open_file_explorer(self):
        '''open file with wxpython dialogue'''

        try:
            dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.filename = dlg.GetFilename()
                self.dirname = dlg.GetDirectory()
                self.control.SetValue(f"{self.dirname}/{self.filename}")
                self.open_file(self.control.GetValue())
                print("file opened")
            dlg.Destroy()
        except Exception as ex:
            print(str(ex))
        finally:
            print("All modifications ended")


    