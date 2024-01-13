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

        except Exception as ex:
            print("Error initializing TopSolid:", ex)

    def disconnect_topsolid(self):
        try:
            if self.design is not None:
                self.design.Disconnect()
                print("Disconnected from TopSolid")
        except Exception as ex:
            print("Error disconnecting from TopSolid:", ex)

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

    def get_constituents(self, folder, printInfo = False):
        folder_const = self.design.Pdm.GetConstituents(folder)
        folder_name = self.get_name(folder)
        
        files = self.check_folder_or_file(folder_const, printInfo)
        

        if printInfo:
            self.print_folder(folder_const, folder_name)

        return files

    def check_folder_or_file(self, folder_const, printInfo = False):
        
        #print("folder path ::")
        ts_files = []

        for file in folder_const[1]:
            self.filter_types(file, printInfo)
            ts_files.append(file)
            #files_names.append(self.get_name(file))

        for dir in folder_const[0]:
            i_files = self.get_constituents(dir)
            #files_names.extend(i_files)

        return ts_files

    def filter_types(self, file, printInfo = False):
        file_type = self.get_type(file)
        match file_type:
            case ".TopPrt":
                type_text = "part file"               
            case ".TopAsm":
                type_text = "assembly file"
            case ".TopDft":
                type_text = "drawing file"
            case ".TopMillTurn":
                type_text = "mill turn file"
            case ".png":
                type_text = "image file"
            case ".jpg":
                type_text = "image file"
            case ".pdf":
                type_text = "pdf file"
            case ".doc":
                type_text = "word file"
            case ".docx":
                type_text = "word file"
            case ".xls":
                type_text = "excel file"
            case ".xlsx":
                type_text = "excel file"
            case ".nc":
                type_text = "nc file"
            case ".iso":
                type_text = "iso file"
            case ".h":
                type_text = "heidenhain file"
            case ".mpf":
                type_text = "siemens SINUMERIK file"
            case ".stp":
                type_text = "3d step file"
            case _:
                type_text = "unknown file type"
        
        if printInfo:
            print(f"{type_text} : {self.get_name(file)} : {file_type}")

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
        file_name = self.get_name(file)
        file_type = self.get_type(file)
        print(msg, " ; ", file_name, " ; ", file_type)

    def print_folder(self, folder_const, folder_name):
        if len(folder_const[0]) > 0 or len(folder_const[1]) > 0:
            print(f"dir {folder_name} @ have ", end="")
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
            '''string titre = "Plan XY";
                string label = "Merci de sélectionner le plan XY du repère";
                UserQuestion QuestionPlan = new UserQuestion(titre, label);
                QuestionPlan.AllowsCreation = true;
                TopSolidHost.User.AskFrame3D(QuestionPlan, true, null, out ReponseRepereUser);
            }'''

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



            '''file explorer functions'''

    def open_file(self):
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


    