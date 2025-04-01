import winreg
import os
import clr
import wx
import logging
from math import pi

import pygetwindow as gw 

from step_file_viewer import StepFileViewer

from tool import Tool
from tool import ToolsDefaultsData
from tool import ToolsCustomData

from databaseTools import update_tool, saveTool

from gui.guiTools import load_masks, GenericMessageBox

clr.AddReference("System.Collections")

from System.Collections.Generic import List

key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

class use_frames:
    named_frames = []
    MCS = None
    CWS = None
    PCS = None
    WCS = None
    CSW = None
    CIP = None
    CIP_tip = None

class TopSolidAPI:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        '''disconnect from TopSolid when exiting context manager and end all modifications'''
        #self.ts.Application.EndModification(True, False)
        if self.editing == True:
            self.end_modif(True, False)
        self.disconnect_topsolid()

    def find_active_window_title(self):
            try:
                window = gw.getWindowsWithTitle('TopSolid 7' )[0]
                return True
            except IndexError:
                logging.error("TopSolid window not found")
                return False
                

    def __init__(self):
        '''initialize TopSolid API'''
        self.ts = None
        self.connected = False
        self.editing = None
        self.current_project = None
        # to select the right tool type on import STEP file
        self.tool = None

        #look open windows to see if TopSolid is already open
        act = self.find_active_window_title()
        if act:
            self._initialize_topsolid()
        

    def _initialize_kernel(self, top_solid_path):
        try:
            top_solid_kernel_sx_path = os.path.join(top_solid_path, "bin", "TopSolid.Kernel.SX.dll")
            clr.AddReference(top_solid_kernel_sx_path)

            top_solid_kernel_path = os.path.join(top_solid_path, "bin", "TopSolid.Kernel.Automating.dll")
            clr.AddReference(top_solid_kernel_path)

            clr.setPreload(True)

            import TopSolid.Kernel.Automating as Automating

            self.auto = Automating
            top_solid_kernel_type = Automating.TopSolidHostInstance
            self.ts = clr.System.Activator.CreateInstance(top_solid_kernel_type)
            
            
            self.ts.Connect()

            if self.ts.IsConnected:
                ts_version = str(self.ts.Version)[:3]
                logging.info(f"TopSolid {ts_version} connected successfully!")
                
                ### self.initialize_ui(top_solid_path)

                return True
            else:
                return False
        except Exception as ex:
            print("Error initializing TopSolid Kernel:", ex)
            return False
        
    def initialize_ui(self, top_solid_path): ################ testing 
        try:
            # Caminho para a DLL
            top_solid_cam = os.path.join(top_solid_path, "bin", "TopSolid.Kernel.WX.dll")

            # Carregar a DLL com clr.AddReference
            clr.AddReference(top_solid_cam)
            clr.setPreload(True)  # Pode ser útil, mas o comportamento exato depende de como o TopSolid gerencia dependências

            # Importar o namespace e a classe desejada
            from TopSolid.Kernel.WX import Application as WX

            try:
                WX.StartApplication()
                WX.CloseAllDocumentWindows()
            except Exception as ex:
                print("Erro ao inicializar a aplicação:", ex)

            document_windows = WX.DocumentWindows
            if document_windows:
                WX.CloseAllDocumentWindows()
            else:
                print("Nenhuma janela de documento aberta.")

                
            # Verifique se existe um documento ativo ou aberto
            if WX.ActiveDocument is not None:
                print("Documento ativo encontrado.")
                # Agora, tente fechar as janelas
                WX.CloseAllDocumentWindows()
            else:
                print("Nenhum documento ativo encontrado.")
            return True

        except Exception as ex:
            print("Error initializing TopSolid Cam:", ex)
            return False
        
    def _initialize_design(self, top_solid_path):
        try:
            top_solid_design_path = os.path.join(top_solid_path, "bin", "TopSolid.Cad.Design.Automating.dll")
            clr.AddReference(top_solid_design_path)
            clr.setPreload(True)
            import TopSolid.Cad.Design.Automating as Automating
            self.ts_d = Automating.TopSolidDesignHostInstance(self.ts)
            self.ts_d.Connect()

            if self.ts_d.IsConnected:
                return True
        except Exception as ex:
            print("Error initializing TopSolid Design:", ex)
            return False

    def _initialize_cam(self, top_solid_path):
        try:
            top_solid_cam = os.path.join(top_solid_path, "bin", "TopSolid.Cam.NC.Kernel.Automating.dll")
            clr.AddReference(top_solid_cam)
            clr.setPreload(True)
            import TopSolid.Cam.NC.Kernel.Automating as Automating
            self.ts_cam = Automating.TopSolidCamHostInstance(self.ts)
            self.ts_cam.Connect()

            if self.ts_cam.IsConnected:
                return True
        except Exception as ex:
            print("Error initializing TopSolid Cam:", ex)
            return False

    def _initialize_topsolid(self):
        '''
        * ts - TopSolidHostInstance 
        * ts_d - TopSolidDesignHostInstance
        * ts_cam - TopSolidCamHostInstance
        '''
        # Get TopSolid registry key path
        key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

        try:
            sub_keys = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            sub_keys_count = winreg.QueryInfoKey(sub_keys)[0]
            top_solid_version = winreg.EnumKey(sub_keys, sub_keys_count - 1)
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path + "\\" + top_solid_version, 0, winreg.KEY_READ)
            value = winreg.QueryValueEx(key, "InstallDir")
            # take the first value, last installed version
            top_solid_path = value[0]

            kernel_initialized = self._initialize_kernel(top_solid_path)
            if kernel_initialized:
                design_initialized = self._initialize_design(top_solid_path)
                cam_initialized = self._initialize_cam(top_solid_path)
                if design_initialized and cam_initialized:
                    self.connected = True
            else:
                self.connected = False


                            
            open_files = self.get_open_files() ### testing
            #bool IsCam(DocumentId inDocumentId)
            #enumerate open cam files
            cam_files = []
            for file in open_files:
                if self.ts_cam.Documents.IsCam(file):
                    #IDocuments.GetMachine Method  
                    # ElementId GetMachine(DocumentId inDocumentId)
                    machine = self.ts_cam.Documents.GetMachine(file)
                    print("machine :: ", self.get_name(machine))
                    
                    #IMachineTools.GetPockets Method 
                    #List<ElementId> GetPockets(ElementId inMachineElementId)
                    pockets = self.ts_cam.Machines.GetPockets(machine)
                    print("pockets :: ", len(pockets))

                    #IMachineTools.GetToolHolders Method  
                    # List<ElementId> GetToolHolders(ElementId inMachineId)
                    holders = self.ts_cam.Machines.GetToolHolders(machine)
                    print("holders :: ", len(holders))

                    #IMachineTools.GetMagazines Method  
                    # List<ElementId> GetMagazines(ElementId inMachineId)
                    magazines = self.ts_cam.Machines.GetMagazines(machine)
                    print("magazines :: ", len(magazines))

                    #IMachineTools.GetPartHolders Method  
                    # List<ElementId> GetPartHolders(ElementId inMachineId)
                    part_holders = self.ts_cam.Machines.GetPartHolders(machine)
                    print("part_holders :: ", len(part_holders))

                    #IMachineTools.GetParameters Method  
                    # List<ParameterId> GetParameters(ElementId inElementId)
                    params = self.ts_cam.Machines.GetParameters(machine)
                    print("params :: ", len(params))

                    print("Cam file :: ", file.PdmDocumentId)
                    cam_files.append(file)
                    tools = self.get_tools(file, True)
                    print(f"tools :: {len(tools)}")

                    #get program from cam file
                    #IPrograms.GetPrograms Method
                    #List<ElementId> GetPrograms(ElementId inDocumentId)
                    programs = self.ts_cam.Programs.GetPrograms(file)
                    print("programs :: ", len(programs))

                    #get program name
                    #string GetName(ElementId inProgramId)
                    program_name = self.ts_cam.Programs.GetName(programs[0])
                    print("program_name :: ", program_name)

                    #get operations from cam file
                    #IPrograms.GetComment Method 
                    #SmartText GetComment(ElementId inProgramId)
                    from TopSolid.Kernel.Automating import SmartText

                    from TopSolid.Cam.NC.Kernel.Automating import ElementExId

                    smartTextType = self.ts_cam.Programs.GetComment(programs[0])
                    print("smartTextType :: ", smartTextType.Value)
                    #get operations from cam file
                    #List<ElementId> GetOperations(ElementId inProgramId)
                    operations = self.ts_cam.Operations.GetOperations(file)
                    print("operations :: ", len(operations))
                    for op in operations:
                        #IOperations.GetDescription Method  
                        #string #GetDescription(ElementExId inElementId)
                        #Public Sub New ( 
                        #    inElementId As ElementId
                        #)
                        ap = ElementExId(op)
                        desc = self.ts_cam.Operations.GetDescription(ap)
                        op_tool = self.ts_cam.Operations.GetTool(ap)
                        tool_name = self.get_name(op_tool.Id)  
                        print(f"OP :: {desc} :: {op_tool.DocumentId.PdmDocumentId } :: {tool_name}")
                       
                        parameters = self.ts_cam.Parameters.GetParameters(ap)
                        print("parameters :: ", len(parameters))
                        pa=0
                        for p in parameters:
                            pa = pa + 1
                            try:
                                name = self.ts_cam.Parameters.GetName(p)
                                ptype = self.ts_cam.Parameters.GetType(p)
                                #<ParameterType.Tool: 6>
                                if name == "Tool":
                                    isTool = self.ts_cam.Tools.IsTool(p)
                                    print(f"param :: {pa} :: {name} :: {isTool} :: type :: {ptype}")
                                    tool_params = self.ts_cam.Tools.GetParameters(p)
                                    print("tool_params :: ", len(tool_params))
                                    for tp in tool_params:
                                        try:
                                            name = self.ts_cam.Parameters.GetName(tp)                                            
                                            print(f"param :: {pa} :: {name} ")
                                        except Exception as ex:
                                            print(f"error :: {pa} :: {name} :: type :: {ptype} :: ", ex)                                            
                                            continue

                                value = self.ts_cam.Parameters.GetValue(p)
                                print(f"param :: {pa} :: {name} :: {value.Value} :: type :: {ptype}")
                            except Exception as ex:
                                print(f"error :: {pa} :: {name} :: type :: {ptype} :: ", ex)
                                
                                continue
                else:
                    print("Design file :: ", file)

            print(f"cam_files :: {len(cam_files)}") 
                

        except Exception as ex:
            print("Error initializing TopSolid:", ex)
            self.connected = False


    def disconnect_topsolid(self):
        try:
            if self.ts is not None:
                self.ts.Disconnect()
                print("Disconnected from TopSolid")
                self.connected = False
        except Exception as ex:
            print("Error disconnecting from TopSolid:", ex)
            self.connected = False

    def get_default_tools_lib(self):
        '''get tools library'''

        # SearchProjectByName -> System.Collections.Generic.List`1[TopSolid.Kernel.Automating.PdmObjectId]
        proj_list = type(self.ts.Pdm.SearchProjectByName("TopSolid Machining User Tools")) #cheat to get type
        proj_list = self.ts.Pdm.SearchProjectByName("TopSolid Machining User Tools")

        # get the id and name of the default tools library
        for lib in proj_list:
            name = self.ts.Pdm.GetName(lib)
            if name == "Outils d'usinage utilisateur TopSolid" or name == "TopSolid Machining User Tools":
                pdmId = lib
                return pdmId, name

    
    def get_ts_language(self):
        '''get TopSolid language'''
        #string CurrentUICultureName { get; }
        culture = None
        if self.ts.IsConnected:
            culture = self.ts.Application.CurrentUICultureName
        return culture
    
    def isDirty(self, docId):
        '''check if document is dirty'''
        # TopSolidHost.Documents.EnsureIsDirty(ref docId);
        return self.ts.Documents.EnsureIsDirty(docId)


    def start_modif(self, op, ot):
        try:
            self.ts.Application.StartModification(op, ot)
            self.editing = True
            logging.info("Start modifications")
        except Exception as ex:
            logging.error(str(ex))
        finally:
            logging.info("All modifications started")

    def end_modif(self, op, ot):
        try:
            #check if modifications are started
            if self.editing or self.editing is None:
                self.ts.Application.EndModification(True, False)
                logging.info("End modifications")
                self.editing = False
            else:  
                logging.info("No modifications to end")

        except Exception as ex:
            logging.error(str(ex))
        finally:
            logging.info("All modifications ended")


    def get_tools(self, doc_id, used = False):
        '''get tools from tools cam file'''


        #toolsList<ElementId> GetTools(DocumentId inDocumentId,bool inUsed)
        tools = self.ts_cam.Documents.GetTools(doc_id, False)
        if tools is not None:
                        
            for t in tools:
                
                #ITools.GetPdmId Method 
                #PdmObjectId GetPdmId(ElementId inToolId)
                pdm_id = self.ts_cam.Tools.GetPdmId(t)
                ### print("pdm_id :: ", pdm_id.Id)
                
                #IDocuments.GetDocument Method 
                #DocumentId GetDocument(PdmObjectId inPdmDocumentId)
                doc_id = self.ts.Documents.GetDocument(pdm_id)

                #testing open tool fimes
                ### self.open_file(doc_id)
                #get name 
                tool_name = self.get_name(doc_id)
                print("tool_name :: ", tool_name)

                #List<ElementId> GetParameters(ElementId inElementId)
                params = self.ts_cam.Tools.GetParameters(t)                
                ###print("params :: ", len(params))

                for p in params: 
                    try:
                        #debug
                        ### print(f"param :: {p.Name} :: {p.ElementId} :: {self.get_type(p.ElementId)}")

                        #double GetPropertyRealValue(ElementId inElementId,string inFullName)
                        #SmartObject GetNamedValue(ElementExId inElementId,string inName)

                        value = self.ts_cam.Parameters.GetNamedValue(p.ElementId, p.Name)
                        #print("value :: ", value)
                        if value is not None:
                            #SmartObject GetValue(ParameterId inParameterId)
                            val = self.ts_cam.Parameters.GetValue(p)
                            ''' p.Name examples
                            $TopSolid.Cam.NC.Kernel.DB.Tools.Entities.Tool.DefinitionDocument.Name  ::  TopSolid.Kernel.Automating.SmartText
                            $TopSolid.Cam.NC.Kernel.DB.Tools.Entities.Tool.DefinitionDocument.ErpPartNumber  ::  TopSolid.Kernel.Automating.SmartText
                            $TopSolid.Cam.NC.Kernel.DB.Tools.Entities.Tool.DefinitionDocument.ManufacturerPartNumber  ::  TopSolid.Kernel.Automating.SmartText
                            '''
                            # extract only the parameter name
                            param_name = p.Name.split(".")[-1]
                            # debug tools parameters
                            ##print(param_name, " :: ", val.Value)

                    except Exception as ex:
                        print("error :: ", ex)
                        continue

                #List<ElementId> GetConstituents(	ElementId inElementId )
        return tools

    def initFolders(self):
        try:
            # Get Topsolid types
            current_project = self.ts.Pdm.GetCurrentProject()
            current_proj_name = self.get_name(current_project)

            proj_const = self.ts.Pdm.GetConstituents(current_project)
            print(f"{str(len(proj_const[0]) - 1)} folders in root project, {str(len(proj_const[1]))} files in root project")

            consts = self.check_folder_or_file(proj_const)
            print("consts :: ", consts)

            return consts

        except Exception as ex:
            # Handle
            print("error :: ", ex)

    
    def read_ts_tools(self, event):
        '''read tools from TopSolid'''
        tools = self.get_tools()
        print("tools :: ", tools)

    def get_constituents(self, proj, printInfo=False):
        '''Get constituents of current project'''
        if proj is None:
            proj = self.ts.Pdm.GetCurrentProject()

        proj_const = self.ts.Pdm.GetConstituents(proj)
        proj_name = self.get_name(proj)
    
        files = self.check_folder_or_file(proj_const, printInfo)
        
        if printInfo:
            self.print_folder(proj_const, proj_name)
        
        return proj, files

    def check_folder_or_file(self, folder_const, printInfo=False):
        files = []
        
        for file in folder_const[1]:
            self.filter_types(file, printInfo)
            files.append(file)
            
        for dir in folder_const[0]:
            folder_name = self.get_name(dir)
            folder_contents = self.get_constituents(dir, printInfo)[1]
            files.append((folder_name, folder_contents))
            
        return files



    def filter_types(self, file, printInfo = False):
        file_type = self.get_type(file)
        #file_type = "(<TopSolid.Kernel.Automating.PdmObjectType object at 0x000001DBE3697EC0>, '.TopPrt')"
        ff = file_type[1]
        match ff:
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
            case ".TopNewPrtSet":
                type_text = "part set"
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
                type_text = "siemens"
            case ".stp":
                type_text = "step"

            case _:
                type_text = "unknown file type"
        
        if printInfo:
            print(f"{self.get_name(file)} : {file_type} :: {type_text}")

    def get_type(self, obj):
        obj_type = type(obj)
        ts_type = ""

        if obj_type is self.auto.PdmObjectId:
            raw_ts_type = self.ts.Pdm.GetType(obj)
            if str(raw_ts_type[0]) == "Folder":
                ts_type = str(raw_ts_type[0])
            else:
               # ts_type = str(self.ts.Pdm.GetType(obj)[1])
               ts_type = self.ts.Pdm.GetType(obj)
        elif obj_type is self.auto.DocumentId:
            #ts_type = str(self.ts.Documents.GetType(obj)[0])
            ts_type = str(self.ts.Documents.GetTypeFullName(obj))
        elif obj_type is self.auto.ElementId:
            ts_type = str(self.ts.Elements.GetTypeFullName(obj))

        return ts_type

    def get_name(self, obj):
        '''get name of object by type, either PdmObjectId, DocumentId or ElementId'''
        if isinstance(obj, (self.auto.PdmObjectId, self.auto.DocumentId, self.auto.ElementId)):
            if obj.IsEmpty is False:
                obj_type = type(obj)
                name = ""
                
                if obj_type is self.auto.PdmObjectId:
                    name = str(self.ts.Pdm.GetName(obj))
                elif obj_type is self.auto.DocumentId:
                    name = str(self.ts.Documents.GetName(obj))
                elif obj_type is self.auto.ElementId:
                    name = str(self.ts.Elements.GetName(obj))

                return name

    def print_info(self, file, msg):
        '''print info about TS object'''
        file_name = self.get_name(file)
        file_type = self.get_type(file)
        print(msg, " ; ", file_name, " ; ", file_type)

    def print_folder(self, folder_const, folder_name):
        if len(folder_const[0]) > 0 or len(folder_const[1]) > 0:
            print(f"folder :: {folder_name} @ have ", end="")
            if len(folder_const[0]) > 0:
                print(f"{len(folder_const[0])} folders ", end="")
            if len(folder_const[1]) > 0:
                print(f"{len(folder_const[1])} files")
            else:
                print("")
        else:
            print(f"dir {folder_name} is empty")

    def get_open_projects(self):
        #List<PdmObjectId> GetOpenProjects(bool inGetsWorkingProjects,bool inGetsLibraryProjects)
        '''get all open projects'''
        projects = self.ts.Pdm.GetOpenProjects(True, False)
        return projects

    def get_current_project(self):
        self.current_project = self.ts.Pdm.GetCurrentProject()
        self.current_proj_id = self.current_project.Id
        #get current project name
        self.current_proj_name = self.get_name(self.current_project)
        #current_proj_name = self.get_name(current_project)
        #return current_project, current_proj_name
    
    
    def is_assembly(self, file):
        '''check if file is assembly'''
        return self.ts_d.Assemblies.IsAssembly(file)
    

    def open_file(self, file):
        '''open file in TopSolid'''
        try:
            #self.ts.Documents.Open(self.ts.Documents.GetDocument(file))
            
            from TopSolid.Kernel.Automating import DocumentId
            # check if type(file) = String
            if isinstance(file, str):
                #public DocumentId(string inPdmDocumentId) 
                file = DocumentId(file)
            res = self.ts.Documents.Open(file)
            print(f"file opened {res}")
        except Exception as ex:
            print(str(ex))
        finally:
            print("INFO :: open_file :: file successfully opened")

    def check_in(self, file):
        '''check in file'''
        #PdmObjectId GetPdmObject( DocumentId inDocumentId )
        pdm_obj = self.ts.Documents.GetPdmObject(file)
       

        print("file to check in :: ", file.PdmDocumentId)
        self.ts.Pdm.CheckIn(pdm_obj, True)

    def check_in_all(self, files):
        '''check in all files in list'''
        #create a list of PdmObjectId
        if isinstance(files, list):
            pdm_obj = List[self.auto.PdmObjectId]()
            for file in files:
                if isinstance(file, self.auto.PdmObjectId):
                    pdm_obj.Add(file)
            self.ts.Pdm.CheckInSeveral(pdm_obj, True)
        else:
            for file in files:
                id = self.ts.Documents.GetPdmObject(file)
                self.ts.Pdm.CheckIn(id, True)


    def ask_plan(self, file):
        '''ask repere of file'''

        try:
            titre = "Plan XY"
            label = "Merci de sélectionner le plan XY du repère"
            QuestionPlan = self.auto.UserQuestion(titre, label)
            QuestionPlan.AllowsCreation = True

            ReponseRepereUser = None            
            ReponseRepereUser = self.ts.User.AskFrame3D(QuestionPlan, True, None, ReponseRepereUser)
            print(ReponseRepereUser)
            if ReponseRepereUser[1]:
                print("plan selected")
                frame = ReponseRepereUser[1]
                print(frame)
                frame_elem_id = frame.ElementId
                print(frame_elem_id)
                frame_name = self.get_name(frame_elem_id)
                print(frame_name)
                return frame

        except Exception as ex:
            print(str(ex))
        finally:
            print("All modifications ended")

    def get_open_files(self, file_type = None):
        '''get open files'''
        try:
            docId = []
            
            tmp = self.ts.Documents.GetOpenDocuments()
            num = len(tmp)
            #print(f"number of open files : {num}")
            if tmp is not None:
                if tmp.Count > 0:
                    for i in tmp:
                        docId.append(i)
                    return docId
                else:
                    return tmp
            
            #print(f"file opened : {docId}")
        except Exception as ex:
            print(str(ex))
        finally:
            print(f"Open files : {num}")
            return docId

    def make_path(self, path):
        try:
            res = os.makedirs(path, exist_ok=True)
            print("MAKE_PATH :: dir created :: ", path, res)
        except Exception as ex:
            # Handle
            print("error :: ", ex)
            pass


    def export_all_pdfs(self, export_path_docs):
        current_project = self.ts.Pdm.GetCurrentProject()
        proj_const = self.ts.Pdm.GetConstituents(current_project)

        for const in proj_const:
            for elem in const:
                elem_name = self.ts.Pdm.GetName(elem)
                elem_type = self.get_type(elem)

                if elem_type == ".TopDft":
                    doc_id = self.ts.Documents.GetDocument(elem)
                    doc_name = self.ts.Documents.GetName(doc_id)

                    self.make_path(export_path_docs)

                    exporter_type = self.ts.Application.GetExporterFileType(10, "outFile", "outExt")  # 10 for pdf
                    complete_path = os.path.join(export_path_docs, f"{doc_name}{exporter_type[1][0]}")

                    export = self.ts.Documents.Export(10, doc_id, complete_path)  # 10 for pdf


    def get_Frames(self, file):
        '''get all frames from file'''
        #IGeometries3D.GetFrames 
        frames = self.ts.Geometries3D.GetFrames(file)

        for frame in frames:
            self.setFrame(frame)

        print("INFO :: get_frames :: ", len(frames), use_frames.named_frames)

        return frames
    
    def setFrame (self, frame):
        #ItemLabel(byte inType,int inId,string inMoniker,string inName)

        name = self.get_name(frame)
        
        frame = self.auto.SmartFrame3D(frame, False)
        #print("setFrame :: ", name)

        if name == "MCS": # machine coordinate system
            use_frames.MCS = frame
        elif name == "CWS": # cutting workpiece system
            use_frames.CWS = frame
        elif name == "PCS": # part coordinate system
            use_frames.PCS = frame
        elif name == "WCS" or name == "$TopSolid.Kernel.DB.D3.Documents.ElementName.AbsoluteFrame": # world coordinate system
            use_frames.WCS = frame
        elif name == "CSW": # tool side holder frame
            use_frames.CSW = frame 
        elif name == "CIP" or name == "CIP_SCHNEIDE": # tool tip frame
            use_frames.CIP = frame
        elif name == "CIP_tip": # tool tip frame
            use_frames.CIP_tip = frame 

        use_frames.named_frames.append(name)
        
    def change_option(self, opt, key, value):
        '''change option in importer options'''
        if opt.Key == key:
            opt.Value = value
            # debug options values
            #print(f"option {key} changed to {value}")
        return opt
    
    def get_importer_options(self, inImporterIx, debug = False): 
        #inImporterIx = type of file to import #10 for .step file
        '''get file importer options'''
        
        opt = self.ts.Application.GetImporterOptions(inImporterIx)

        # Create a copy of the list by iterating over it
        opt_copy = [item for item in opt]

        for i, item in enumerate(opt_copy):
            if item.Key == "SIMPLIFIES_GEOMETRY" or item.Key == "SEWS_SHEETS" or item.Key == "TRANSLATES_MATERIAL":
                opt[i] = self.change_option(item, item.Key, "True")
            elif item.Key == "TRANSLATES_ASSEMBLY":
                opt[i] = self.change_option(item, item.Key, "False")
            elif item.Key == "ASSEMBLY_DOCUMENT_EXTENSION":
                opt[i] = self.change_option(item, item.Key, ".TopPrt")
            else:
                opt[i] = self.change_option(item, item.Key, item.Value)

        # debug options values    
        for item in opt:
            print(f"option {item.Key} : {item.Value}")

        return opt
                

    def exec_import(self, inImporterIx, inFullName, inOwnerId):  
        '''execute import with options'''

        uop = ""
        out = ""

        file_type = self.ts.Application.GetImporterFileType(inImporterIx, uop, out) #inImporterIx = type of file to import
        print(f"file type to import :: {file_type} :: {inImporterIx} :: {uop} :: {out}")

        set_opt = self.get_importer_options(inImporterIx)
                        
        result = self.ts.Documents.ImportWithOptions(inImporterIx, set_opt ,  inFullName[0],  inOwnerId)

        print(f"Import result: {len(result)} - {result[0]} -- {result[1]} -- {result[2]}")

        return result
    
        ''' Default options 716
        0 TRANSLATES_ASSEMBLY True
        1 TRANSLATES_ATTRIBUTES True
        2 SIMPLIFIES_GEOMETRY True
        3 SEWS_SHEETS True
        4 LINEAR_TOLERANCE 1E-02 # default: 1E-05 = 0.00001 / 1E-01 = 0.1 / 1E-02 = 0.01 
        5 BODY_DOCUMENT_EXTENSION .TopPrt
        6 ASSEMBLY_DOCUMENT_EXTENSION .TopPrt
        7 TRANSLATES_FREE_CURVES True
        8 TRANSLATES_FREE_SURFACES True
        9 TRANSLATES_HIDDEN_ENTITIES False
        10 IMPORTS_PMI True
        11 TRANSLATES_MATERIAL False
        12 DEEP_HEALING False
        13 IS_TRANSLATOR_SILENT False
        '''

    def create_frames_from_step(self, step_viewer, newdoc, found_elements):
        print("INFO :: frames < found_elements")
                
            # Get the absolute frame of the document #ElementId GetAbsoluteFrame(DocumentId inDocumentId)
            #abs_smartFrame = self.ts.Geometries3D.GetAbsoluteFrame(newdoc[0])

            # cycle through the found elements of the step file and create frames if they don't exist
        for name, placement in found_elements.items():
            #check if the frame already exists
            if name not in use_frames.named_frames or name == "CIP" or name == "CIP_SCHNEIDE":
                print("frame not  exists")
                
                print(f"Found {name} :: {placement.name} : {placement.coord} : {placement.dir_z} : {placement.dir_x}")

                # Get the direction and 3d coords origin of the frame from the step file
                direction_z = self.auto.Direction3D(placement.dir_z.x, placement.dir_z.y, placement.dir_z.z)
                direction_x = self.auto.Direction3D(placement.dir_x.x, placement.dir_x.y, placement.dir_x.z)                        
                p3d = self.auto.Point3D(placement.coord.x, placement.coord.y, placement.coord.z)
                                
                #need to calculate the the direction_y
                #public static Vector3D operator ^(Direction3D inDirection1,Direction3D inDirection2)
                vector_y = (direction_z  ^ direction_x)

                #vector 2 direction
                #public static explicit operator Direction3D (Vector3D inVector)
                direction_y = self.auto.Direction3D(vector_y.X, vector_y.Y, vector_y.Z)

                new_frame = self.auto.Frame3D(p3d, direction_x,  direction_y, direction_z) 
                new_name = f"{name}"

                #create a new frame with the same name if not exists
                if name == "CIP" or name == "CIP_SCHNEIDE" and self.tool:
                    print("INFO :: tool frame rotation")
                    # inverted -direction_y and direction_z to get the right orientation
                    # Frame3D Frame3D(Point3D inOrigin,Direction3D inXDirection,Direction3D inZDirection,Direction3D inYDirection)
                    new_frame = self.auto.Frame3D(p3d, direction_x,  direction_z, -direction_y)     
                    new_name = f"{name}_tip"

                created_frame = self.ts.Geometries3D.CreateFrame(newdoc, new_frame)
                print("created_frame :: ", created_frame)
                # SetName(ElementId inElementId,string inName)
                f_name = self.ts.Elements.GetFriendlyName(created_frame)
                self.ts.Elements.SetName(created_frame, new_name)
                print("f_name :: ", f_name, name)
                self.setFrame(created_frame)

    def close_file(self, file):
        '''close file in TopSolid'''
        try:
            self.ts.Documents.Close(file, False, True)
        except Exception as ex:
            print(str(ex))
        finally:
            print("INFO :: close_file :: file successfully closed")

    def Import_file_w_conv(self, inImporterIx, inFullName, inOwnerId):
        '''import file with conversion'''

        print("INFO :: import file with conversion :: type :: ", inImporterIx, " :: name :: " , inFullName)
        
        outLog = []
        outBadDocumentIds = [self.auto.DocumentId]

        try:            
            step_viewer = StepFileViewer()
            # load the step file
            print("INFO :: file loaded :: ", inFullName)
            step_viewer.loadStepFile(inFullName[0])

            # search for the axis2 elements in the step file
            found_elements , brep_name = step_viewer.findPlacementElements()

            #check if there are any elements found, and if its an holder or tool
            if len(found_elements) > 0:
                #check if its a holder or tool
                if "CIP" in found_elements:
                    print("Tool found")
                    self.tool = True
                else:
                    print("Holder found")
                    self.tool = False
                
            print(f"Found {len(found_elements)} named 2AxisPlacement3D")

            result = self.exec_import(inImporterIx, inFullName, inOwnerId)
            newdoc = result[0]  

            # ************************************************************************************************
            # Read frames after the import
            # ************************************************************************************************

            frames = []
            use_frames.MCS = None
            use_frames.CWS = None
            use_frames.PCS = None
            use_frames.WCS = None
            use_frames.CSW = None


            #open the file
            print("get_Frames :: ", len(frames))

            self.open_file(newdoc[0])
                        
            self.start_modif("frame", False)
            drt = self.ts.Documents.EnsureIsDirty(newdoc[0])
            newdoc[0] = drt
            frames = self.get_Frames(newdoc[0])                            

            print("INFO :: frames :: ", len(frames), use_frames.named_frames)

            if len(found_elements) > 0:
                self.create_frames_from_step(step_viewer, newdoc[0], found_elements)
            elif len(frames) <= 1:
                print("INFO :: step file not full supported, {len(frames)} frames found")
                new_plan = self.ask_plan(newdoc[0])
                use_frames.CSW = new_plan
                
                              
            # Read shapes in the file
                
            #List<ElementId> GetShapes(DocumentId inDocumentId)                    
            shapes = self.ts.Shapes.GetShapes(newdoc[0])
            print("***************************************************************")
            print("shapes :: ", shapes, len(shapes))
            if len(shapes) > 1:
                for shape in shapes:
                    shape_name = self.get_name(shape) + "_shape"
                    shape_type = self.get_type(shape)
                    print(shape_name, shape_type, self.ts.Shapes.GetShapeType(shape))
                    
                    if str(shape_name) == "CUT":
                        self.tool = True
                        tool = Tool()
                        print("INFO :: n of faces :: ", self.ts.Shapes.GetFaceCount(shape))

                        faces = self.ts.Shapes.GetFaces(shape)
                        cut_len = []
                        circles_radius = []

                        for face in faces:
                            face_type = self.ts.Shapes.GetFaceSurfaceType(face)
                            print(f"{face} :: {face_type} :: {len(faces)}")
                            #List<ElementItemId> GetFaceConnectedFaces(ElementItemId inFaceId)
                            connected_faces = self.ts.Shapes.GetFaceConnectedFaces(face)
                            print("connected_faces :: ", connected_faces, len(connected_faces))
                            face_range = self.ts.Shapes.GetFaceRange(face)
                            print("face_range :: ", face_range)

                            #List<ElementItemId> GetFaceEdges(ElementItemId inFaceId)
                            edges = self.ts.Shapes.GetFaceEdges(face)
                            print("******************** edges :: ", edges, len(edges))

                            for edge in edges:
                                # CurveType GetEdgeCurveType(ElementItemId inEdgeId)
                                c_type = self.ts.Shapes.GetEdgeCurveType(edge)
                                # Point3D GetEdgePoint(ElementItemId inEdgeId,double inT)
                                e_point = self.ts.Shapes.GetEdgePoint(edge, 0.0)
                                print("edge :: ", edge, c_type, e_point.X, e_point.Y, e_point.Z, e_point.P0.X, e_point.P0.Y, e_point.P0.Z)
                                cut_len.append(e_point.Z)
                                # void GetEdgeVertices(ElementItemId inEdgeId,out ElementItemId outStartVertexId,out ElementItemId outEndVertexId)
                                start_vertex, end_vertex = self.ts.Shapes.GetEdgeVertices(edge)
                                print("start_vertex :: ", start_vertex, "end_vertex :: ", end_vertex)
                                # double GetEdgeLength(ElementItemId inEdgeId)
                                e_length = self.ts.Shapes.GetEdgeLength(edge)
                                print("e_length :: ", e_length)

                                if str(c_type) == "Circle":
                                    # void GetEdgeCircleCurve(ElementItemId inEdgeId,out Plane3D outPlane,out double outRadius)
                                    circle , c_radius = self.ts.Shapes.GetEdgeCircleCurve(edge)
                                    print("circle :: ", circle, c_radius)
                                    circles_radius.append(c_radius)

                        print("cut_len :: ", cut_len, circles_radius)
                        #take the max value of the list and get de diference between the max and min value, and round to 3 decimal places
                        tool.L1 = round((max(cut_len) - min(cut_len)), 3)
                        print("dif :: ", tool.L1 * 1000)
                        #to radius of the circle we need to take the max, but stay on test
                        tool.D1 = round(max(circles_radius), 3)*2

                        print("INFO :: n of edges :: ", self.ts.Shapes.GetEdgeCount(shape))
                        edges = self.ts.Shapes.GetEdges(shape)
                        for edge in edges:
                            print(edge)
                        print("INFO :: n of vertices :: ", self.ts.Shapes.GetVertexCount(shape))
                        vertices = self.ts.Shapes.GetVertices(shape)
                        for vertex in vertices:
                            print(vertex)

                        '''
                        void GetFaceEnclosingCoordinates(
                                                            ElementItemId inFaceId,
                                                            out double outXmin,
                                                            out double outXmax,
                                                            out double outYmin,
                                                            out double outYmax,
                                                            out double outZmin,
                                                            out double outZmax
                                                            )'''
                    
                        #public ElementItemId(ElementId inElementId,ItemLabel inItemLabel)
                        #eii = self.auto.ElementItemId(shape, self.auto.ItemLabel(0, 0, "CUT", "CUT"))
                        
                        print("Multiple shapes found, 'CUT' shape found, is a tool :: D1 :: ", tool.D1 * 1000, "L1 :: ", tool.L1 * 1000)
                        
                if not self.tool:
                    print("Multiple shapes found, no 'CUT' shape, is a holder")
            
            else:
                print("One shape found, no tool found, is a holder")
                self.tool = False

            #**************************************************************
            # need to check if is a tool or holder before begin the process
            #**************************************************************
            # if tool need 2 shapes, 2 revolved sketches
            # if holder need 1 shape, 1 revolved sketch

            print("is tool? :: ", self.tool)

            axis = self.ts.Geometries3D.GetAxes(newdoc[0])
            print("axis :: ", len(axis))

            '''
            for ax in axis:
                print(self.get_name(ax))

            output:
            $TopSolid.Kernel.DB.D3.Documents.ElementName.AbsoluteXAxis
            $TopSolid.Kernel.DB.D3.Documents.ElementName.AbsoluteYAxis
            $TopSolid.Kernel.DB.D3.Documents.ElementName.AbsoluteZAxis
            '''
            #get Z axis
            newAxis = self.auto.SmartAxis3D(axis[2],  False) # x = 0, y = 1, z = 2

            #print("newAxis :: ", newAxis, self.get_name(newAxis))

            #get the shape to revolve
            for shape in shapes:
                shape_name = self.get_name(shape)
                print("shape_name :: ", shape_name)
                shape = self.auto.SmartShape(shape)

                '''
                for plane3d in planes:
                    print(self.get_name(plane3d))

                output:
                $TopSolid.Kernel.DB.D3.Documents.ElementName.AbsoluteXYPlane
                $TopSolid.Kernel.DB.D3.Documents.ElementName.AbsoluteXZPlane
                $TopSolid.Kernel.DB.D3.Documents.ElementName.AbsoluteYZPlane
                '''
                #get the absolute XZ plane
                plane = self.ts.Geometries3D.GetAbsoluteXZPlane(newdoc[0])

                #need a SmartPlane3D to use in the CreateSketchIn3D method
                splane = self.auto.SmartPlane3D(plane, False)

                # ElementId CreateSketchIn3D( DocumentId inDocumentId, SmartPlane3D inPlane, SmartPoint3D inOrigin, bool inDefinesXDirection, SmartDirection3D inDirection )
                sketch = self.ts.Sketches2D.CreateSketchIn3D(newdoc[0], splane,  self.auto.SmartPoint3D(self.auto.Point3D(0, 0, 1)), True, self.auto.SmartDirection3D(self.auto.Direction3D(1, 0,0), self.auto.Point3D(1, 0, 0)))
                
                self.ts.Sketches2D.StartModification(sketch)

                #ElementId CreateRevolvedSilhouette(SmartShape inShape,SmartAxis3D inAxis,bool inMerge)
                revolved = self.ts.Sketches2D.CreateRevolvedSilhouette(shape, newAxis, True)
                #set the name of the revolved sketch
                #put shape_name into minus case
                minus_shape_name = shape_name.lower() + "_revolved"
                #check if the name is numeric, so it cant be in minus case
                if minus_shape_name.isnumeric():
                    minus_shape_name = f"shape_{minus_shape_name}"
                self.ts.Elements.SetName(sketch, minus_shape_name)

                print("revolved :: ", revolved)

                self.ts.Sketches2D.EndModification()

            #SearchProjectByName(string inProjectName)
            func_proj =  self.ts.Pdm.SearchProjectByName("TopSolid Machining")
            print("func_proj :: ", func_proj, len(func_proj))

            for func in func_proj:
                print(self.get_name(func), self.get_type(func))
                if self.get_name(func) == "Usinage TopSolid" or self.get_name(func) == "TopSolid Machining":
                    func_proj = func
                    break
            
            if self.tool :
                print("INFO :: add tool functions")

                '''      
                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Fraise 2 tailles")
                print("ts_func :: ", ts_func, len(ts_func), self.get_name(ts_func[0]))
                func_doc = self.ts.Documents.GetDocument(ts_func[0])
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Fraise 2 tailles")

                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Attachement cylindrique outil")
                print("ts_func :: ", ts_func, len(ts_func), self.get_name(ts_func[0]))
                func_doc = self.ts.Documents.GetDocument(ts_func[0])
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Attachement cylindrique outil")
                '''

                self.provide_tool_function(newdoc[0], func_proj, "Fraise 2 tailles")
                self.provide_tool_function(newdoc[0], func_proj, "Attachement cylindrique outil")
                self.provide_tool_function(newdoc[0], func_proj, "Profil de révolution pour l'analyse de collision")          
                self.provide_tool_function(newdoc[0], func_proj, "Profil de révolution pour mise à jour du brut")

                functions = self.ts.Entities.GetFunctions(newdoc[0])

                #List<ElementId> GetSketches( DocumentId inDocumentId )
                sketches = self.ts.Sketches2D.GetSketches(newdoc[0])
                print("sketches :: ", sketches, len(sketches))
        
                print("functions :: ", functions, len(functions))
                for f in functions:
                    # List<ElementId> GetFunctionPublishings(ElementId inElementId)
                    func_pubs = self.ts.Entities.GetFunctionPublishings(f)
                    # string GetFunctionOccurrenceName(ElementId inElementId)
                    func_pub_name = self.ts.Entities.GetFunctionOccurrenceName(f)
                    print("func_pubs :: ", func_pub_name, len(func_pubs))

                    for pub in func_pubs:
                        p_name = self.get_name(pub)
                        print("INFO :: function found :: ", p_name, self.get_type(pub))
                        '''
                            Fraise 2 tailles
                                Function Use TopSolid.Kernel.DB.Parameters.PublishingEnumerationParameterEntity
                                CuttingEdgeOrigin TopSolid.Kernel.DB.D3.Frames.PublishingFrameEntity
                                CenterCutting TopSolid.Kernel.DB.Parameters.PublishingBooleanParameterEntity
                                MaximumRampAngle TopSolid.Kernel.DB.Parameters.PublishingRealParameterEntity
                                CoolantNozzle TopSolid.Kernel.DB.Parameters.PublishingBooleanParameterEntity
                                NumberOfToolTeeth TopSolid.Kernel.DB.Parameters.PublishingIntegerParameterEntity
                                LeftHand TopSolid.Kernel.DB.Parameters.PublishingBooleanParameterEntity
                                CuttingToolMaterialCategory TopSolid.Kernel.DB.Parameters.PublishingEnumerationParameterEntity
                                CuttingLength TopSolid.Kernel.DB.Parameters.PublishingRealParameterEntity
                                CuttingDiameter TopSolid.Kernel.DB.Parameters.PublishingRealParameterEntity

                            Attachement cylindrique outil
                                Function Use TopSolid.Kernel.DB.Parameters.PublishingEnumerationParameterEntity
                                MaximalDistance TopSolid.Kernel.DB.Parameters.PublishingRealParameterEntity
                                MinimalDistance TopSolid.Kernel.DB.Parameters.PublishingRealParameterEntity
                                InitialDistance TopSolid.Kernel.DB.Parameters.PublishingRealParameterEntity
                                ShankDiameter TopSolid.Kernel.DB.Parameters.PublishingRealParameterEntity
                                ToolingSystemFrame TopSolid.Kernel.DB.D3.Frames.PublishingFrameEntity
                            
                            Profil de révolution pour l'analyse de collision
                                Function Use TopSolid.Kernel.DB.Parameters.PublishingEnumerationParameterEntity
                                Revolute Section TopSolid.Kernel.DB.D3.Sections.PublishingSectionEntity
                     
                        if str(p_name) == "Function Use":
                            id = self.ts.Parameters.GetEnumerationPublishingDefinition(pub)
                            print("id :: ", id, id.Value)
                            id.Value = 3
                            #IParameters.SetEnumerationPublishingDefinition Method
                            self.ts.Parameters.SetEnumerationPublishingDefinition(pub, id)
                        '''

                        if p_name == "CuttingDiameter":
                            #IParameters.SetRealPublishingDefinition Method
                            if  tool.D1 is not None:
                                self.ts.Parameters.SetRealPublishingDefinition(pub, self.auto.SmartReal(self.auto.UnitType.Length, tool.D1))
                        elif p_name == "CuttingLength":
                            #IParameters.SetRealPublishingDefinition Method
                            if  tool.L1 is not None:
                                self.ts.Parameters.SetRealPublishingDefinition(pub, self.auto.SmartReal(self.auto.UnitType.Length, tool.L1))
                        elif p_name == "CuttingEdgeOrigin":
                            #IParameters.SetFramePublishingDefinition Method
                            self.ts.Geometries3D.SetFramePublishingDefinition(pub, use_frames.CIP_tip)
                        elif p_name == "ToolingSystemFrame":
                            #IParameters.SetFramePublishingDefinition Method
                            self.ts.Geometries3D.SetFramePublishingDefinition(pub, use_frames.MCS)
                        elif p_name == "Revolute Section":                                                        
                            for sketch in sketches:
                                sketch_name = self.get_name(sketch)                                
                                if  sketch_name == "nocut":
                                    ##print("INFO :: sketch found :: ", sketch_name)
                                    #public SmartSection3D(ElementId inElementId)
                                    sect = self.auto.SmartSection3D(sketch)
                                    #print("sect :: ", sect, self.get_name(sect))
                                    #void SetSectionPublishingDefinition(ElementId inElementId,SmartSection3D inDefinition)
                                    self.ts.Geometries3D.SetSectionPublishingDefinition(pub, sect)
                                    break

                        elif p_name == "Revolution Section":
                            for sketch in sketches:
                                sketch_name = self.get_name(sketch)
                                if  sketch_name == "cut":
                                    ##print("INFO :: sketch found :: ", sketch_name)
                                    #public SmartSection3D(ElementId inElementId)
                                    sect = self.auto.SmartSection3D(sketch)
                                    #print("sect :: ", sect, self.get_name(sect))
                                    #void SetSectionPublishingDefinition(ElementId inElementId,SmartSection3D inDefinition)
                                    self.ts.Geometries3D.SetSectionPublishingDefinition(pub, sect)                                
                                    break

            else: 
                ##print("INFO :: add holder functions")
                #get function PdmDocumentId by Name
                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Attachement cylindrique porte outil")              
                ##print("ts_func :: ", ts_func, len(ts_func), self.get_name(ts_func[0]))
                #Get DocumentId by PdmObjectId
                func_doc = self.ts.Documents.GetDocument(ts_func[0])         
                #ElementId ProvideFunction( DocumentId inDocumentId,DocumentId inFunctionId,string inOccurrenceName)                
               
                #prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Attachement cylindrique porte outil")
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "CylindricalToolingHolder_1")

                # IGeometries3D - void SetFramePublishingDefinition( inElementId,SmartFrame3D inDefinition)
                        #self.design.Geometries3D.SetFramePublishingDefinition(prov_func, use_frames.CSW)
                
                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Profil de révolution pour l'analyse de collision")
                ##print("ts_func :: ", ts_func, len(ts_func))
                func_doc = self.ts.Documents.GetDocument(ts_func[0])
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "CollisionAnalysisRevolutionShape_1")
                
                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Système de fixation outil")
                ##print("ts_func :: ", ts_func, len(ts_func))
                func_doc = self.ts.Documents.GetDocument(ts_func[0])
                #prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Système de fixation vers la machine")
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "ToolingShank_1")
                
                #List<ElementId> GetFunctions( DocumentId inDocumentId )                
                functions = self.ts.Entities.GetFunctions(newdoc[0])
                
                ##print("functions :: ", functions, len(functions))
                for func in functions:
                    ##print(self.get_name(func))
                    #GetFunctionDefinition(	ElementId inElementId)
                    func_def = self.ts.Entities.GetFunctionDefinition(func)
                    ##print("func_def :: ", func_def, self.get_name(func_def))

                    #GetFunctionOccurrenceName(	ElementId inElementId ) as String
                    func_occ = self.ts.Entities.GetFunctionOccurrenceName(func)
                    ##print("func_occ :: ", func_occ)

                    #GetFunctionPublishings(ElementId inElementId) as List<ElementId>
                    func_pubs = self.ts.Entities.GetFunctionPublishings(func)
                    ##print("func_pubs :: ", func_pubs, len(func_pubs))

                    #self.start_modif("func", False)

                    for pub in func_pubs:
                        ##print("INFO :: function found :: ", self.get_name(pub), self.get_type(pub))
                        '''
                        ToolingSystemFrame -> Frame PCS ( tool side )
                        ToolingSystemName -> Frame or Text - machine side ( link to machine )
                        ToolingSystemSize -> Real - holder link size to machine side
                        ToolingSystemType -> Text - holder type
                        Revolute Section -> Section - holder collision revolute section
                        Function Use -> Enumeration - holder function use
                        '''

                        if self.get_name(pub) == "ToolingSystemFrame":
                            #SetFramePublishingDefinition( inElementId,SmartFrame3D inDefinition)
                            if use_frames.PCS is not None:
                                self.ts.Geometries3D.SetFramePublishingDefinition(pub, use_frames.PCS)
                            elif use_frames.WCS is not None:
                                self.ts.Geometries3D.SetFramePublishingDefinition(pub, use_frames.WCS)
                        elif self.get_name(pub) == "ToolingSystemName":
                            pub_type = self.get_type(pub)
                            #print("pub_type :: ", pub_type)
                            if pub_type == "TopSolid.Kernel.DB.D3.Frames.PublishingFrameEntity":
                                #if use_frames.CSW is not None:
                                if use_frames.CSW is not None:
                                    self.ts.Geometries3D.SetFramePublishingDefinition(pub, use_frames.CSW)
                                else:
                                    #get absolute frame
                                    frame = self.ts.Geometries3D.GetAbsoluteFrame(newdoc[0])
                                    #set the absolute frame to smartframe3d
                                    frame = self.auto.SmartFrame3D(frame, False)
                                    self.ts.Geometries3D.SetFramePublishingDefinition(pub, frame)
                            else:
                                #IParameters.SetTextPublishingDefinition Method  
                                pub_name = self.auto.SmartText("HSK")
                                self.ts.Parameters.SetTextPublishingDefinition(pub, pub_name)
                        elif self.get_name(pub) == "ToolingSystemSize":
                            pub_size = self.auto.SmartReal(self.auto.UnitType.Length, (63/1000)) 
                            #IParameters.SetTextPublishingDefinition Method
                            self.ts.Parameters.SetRealPublishingDefinition(pub, pub_size)
                        elif self.get_name(pub) == "ToolingSystemType":
                            #pub_name = self.auto.SmartText("Mandrin pour queue cylindrique")
                            pub_name = self.auto.SmartText(func_occ)
                            
                            self.ts.Parameters.SetTextPublishingDefinition(pub, pub_name)
                        elif self.get_name(pub) == "Revolute Section":
                            #List<ElementId> GetSketches( DocumentId inDocumentId )
                            print("INFO :: revolute section found :: ", len(newdoc))
                            sketches = self.ts.Sketches2D.GetSketches(newdoc[0])
                            #
                            print("sketches :: ", self.get_name(sketches[0]), len(sketches))
                            #public SmartSection3D(ElementId inElementId)
                            sect = self.auto.SmartSection3D(sketches[0])
                            #print("sect :: ", sect, self.get_name(sect))
                            #void SetSectionPublishingDefinition(ElementId inElementId,SmartSection3D inDefinition)
                            self.ts.Geometries3D.SetSectionPublishingDefinition(pub, sect)
                        elif self.get_name(pub) == "Function Use": 
                            print("INFO :: function found :: ", self.get_name(pub))
                            # IParameters
                            # SmartUserEnumeration GetUserEnumerationPublishingDefinition(ElementId inElementId)
                            id = self.ts.Parameters.GetEnumerationPublishingDefinition(pub)
                            # int GetEnumerationValue(ElementId inElementId)
                            val = self.ts.Parameters.GetEnumerationValue(pub)                            
                            print("id :: ", id, id.EnumGuid, val)
                            # public class SmartEnumeration : SmartObject
                                # EnumGuid, ItemLabel, ElementId, value
                            # public Guid EnumGuid
                            guid = id.EnumGuid
                            #print("guid :: ", guid)
                            enum = self.auto.SmartEnumeration(id.EnumGuid, 2)

                            # void SetEnumerationPublishingDefinition( ElementId inElementId, SmartEnumeration inDefinition )
                            self.ts.Parameters.SetEnumerationPublishingDefinition(pub, enum) 
                            
                        print("pub :: ", pub, self.get_name(pub))            

            smartTextType = self.auto.SmartText(self.ts.Parameters.GetDescriptionParameter(newdoc[0]))

            self.ts.Parameters.PublishText(newdoc[0], "PO", smartTextType)

            #need elementId
            #tool = self.ts_cam.Tools.GetParameters(newdoc[0].Id)

            #for p in tool:
                #print(p)

            #end_modif
            self.end_modif(True, False)

            # Convertendo os resultados para tipos de dados padrão do Python
            outLog_python = list(outLog)
            outBadDocumentIds_python = list(outBadDocumentIds)

            return result, outLog_python, outBadDocumentIds_python
        except Exception as e:
            print(f"Error importing documents: {e}")
            self.end_modif(True, False)
            raise

    def provide_tool_function(self,doc, func_proj, function):
        '''need funtion to add tool functions'''
        ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, function)
        print("ts_func :: ", ts_func, len(ts_func), self.get_name(ts_func[0]))
        func_doc = self.ts.Documents.GetDocument(ts_func[0])
        prov_func = self.ts.Entities.ProvideFunction(doc, func_doc, function)
        

    def read_functions(self, file):
        '''read function from file'''
        self.start_modif("func", False)
        #List<ElementId> GetFunctions( DocumentId inDocumentId )
        functions = self.ts.Entities.GetFunctions(file)
        print("functions :: ", functions, len(functions))
        try:
            for func in functions:
                print(self.get_name(func))
                #GetFunctionDefinition(	ElementId inElementId)
                func_def = self.ts.Entities.GetFunctionDefinition(func)
                print("func_def :: ", func_def, self.get_name(func_def))

                #GetFunctionOccurrenceName(	ElementId inElementId ) as String
                func_occ = self.ts.Entities.GetFunctionOccurrenceName(func)
                print("func_occ :: ", func_occ)

                #GetFunctionPublishings(ElementId inElementId) as List<ElementId>
                func_pubs = self.ts.Entities.GetFunctionPublishings(func)
                print("func_pubs :: ", func_pubs, len(func_pubs))

                for pub in func_pubs:
                    print("INFO :: function found :: ", self.get_name(pub), self.get_type(pub))
                    if self.get_name(pub) == "Function Use": 
                        # IParameters
                        # SmartUserEnumeration GetUserEnumerationPublishingDefinition(ElementId inElementId)
                        id = self.ts.Parameters.GetEnumerationPublishingDefinition(pub)
                        # int GetEnumerationValue(ElementId inElementId)
                        val = self.ts.Parameters.GetEnumerationValue(pub)                            
                        print("id :: ", id, id.EnumGuid, val)

        except Exception as ex:
            self.end_modif(True, False)
            print(str(ex))


    def searchHolder(self, file):
        '''search holder in open files'''
        holders = []
        for holder in file:
            print("check holder: ", holder.PdmDocumentId)
            #check if it not an assembly, because holder is one part
            if self.ts_d.Assemblies.IsAssembly(holder) == False:
                if self.ts_d.Parts.IsPart(holder) == True:
                    #get functions of the part
                    holderFunctions = self.ts.Entities.GetFunctions(holder)
                    if holderFunctions:
                        print("number functions found: ", len(holderFunctions))
                        if holderFunctions and len(holderFunctions) > 0:
                            for  i in holderFunctions:
                                function = str(self.ts.Elements.GetFriendlyName(i))
                                print(f"GetName: {self.ts.Elements.GetName(i)} GetFriendlyName:  {function}")
                                #if function == "Système de fixation porte-outil <ToolingHolder_1>" or function == "Attachement cylindrique porte outil <CylindricalToolingHolder_1>" or function == "Attachement cylindrique porte outil <ToolingHolder_1>" or function == "Attachement cylindrique porte outil <Attachement cylindrique pour l'outil>" or function == "Tooling Shank <Système de fixation outil>": #TODO: check if exist a better way to identify holder
                                #check if function is a holder by get first words "Tooling Shank"
                                #if function.startswith("Tooling Shank") or function.startswith("Attachement cylindrique porte outil") or function.startswith("Système de fixation porte-outil") or function.startswith("Attachement cylindrique pour l'outil") or function.startswith("Attachement cylindrique porte outil  <ToolingHolder_1>"):
                                if function.startswith("Attachement cylindrique porte outil") or function.startswith("Système de fixation porte-outil"):

                                    print(f"found : {function}")
                                    holders.append(holder)
                                    #create_tool_w_holder(api.ts ,api.ts_d , output_lib, tool, holder)
                                    break
                                elif function == "Compensation outil <TO>":
                                    print(f"not an holder : {function} is one tool")
                                    break
        return holders

    def insert_into_holder(self, tool):
        '''insert tool into holder'''        
        try:
            proj = self.get_current_project()
            #get open files
            open_files = self.get_open_files()
            print(f"INFO :: current project :: {self.current_proj_name} :: open files ::  {len(open_files)}")
            
            if len(open_files) == 0:
                #msg box theres no open holder in TS
                output_msg = wx.MessageBox('no files open on TS, try to open an holder and retry', 'Warning', wx.OK | wx.CANCEL | wx.ICON_QUESTION)                      
            
            #check if any holder is open in TS
            holders = self.searchHolder(open_files)
            
            if len(holders) > 0:
                for holder in holders:
                    self.add_tool_to_holder(self.current_project, tool, holder)
                return True
            else:
                noTool = wx.MessageBox('holder not open on TS, try to open and retry', 'Warning', wx.OK |wx .CANCEL | wx.ICON_QUESTION)
                if noTool == wx.OK:
                    self.insert_into_holder(tool)
                print("noTool: ", noTool)
                return False


        except Exception as ex:
            # msg box error copying tool
            dialog = wx.MessageBox('Error copying tool: ' + str(ex), 'Warning', wx.OK_DEFAULT | wx.ICON_ERROR)

            print("Error copying tool: " + str(ex))
            self.end_modif(True, False)
            return False


    def add_tool_to_holder(self, output_lib, tool, holder): #holder = true or false
        '''add tool to holder'''
        
        from TopSolid.Kernel.Automating import DocumentId

        print(f"INFO :: include {tool.name} into {self.get_name(holder)} ::  {tool.TSid}")                                                  

        elemModelId = []
        elemModelId.append(holder)

        #get the assembly model
        print("output_lib: ", output_lib.Id)
        
        assemblyModelId = self.ts.Pdm.SearchDocumentByName(output_lib, "FR + PO") #TODO: make it editable

        print("tset: ", assemblyModelId, len(assemblyModelId))
        if len(assemblyModelId) == 0:
            print("assembly not found. need to import/create it?")
            #TODO: add a dialog to select to create or not
            resp = wx.MessageBox('assembly not found. need to import/create it?', 'Warning', wx.YES_NO | wx.ICON_QUESTION)
            return
        
        else:
            print("assemblyModelId: ", assemblyModelId[0].Id)
                            
            elemModelId.append(DocumentId(tool.TSid))  

            print("elemModelId",elemModelId, len(elemModelId))
            for i in elemModelId:
                print("elemModelId: ", i)

            # need a list of PdmObjectId to CopySeveral, but we need to copy only the first tool
            firstTool = assemblyModelId[0]
            assemblyModelId.Clear()
            assemblyModelId.Add(firstTool)

            #PdmObjectId CreateDocument(PdmObjectId inOwnerId,string inExtension,bool inUseDefaultTemplate)
            new_assembly = self.ts.Pdm.CreateDocument(assemblyModelId[0], ".TopAsm", True)

            newTool =  self.ts.Pdm.CopySeveral(assemblyModelId, output_lib)

            print(f"Tool copied successfully! {newTool[0].Id}")
            
            newToolDocId = self.ts.Documents.GetDocument(newTool[0])

            self.ts.Documents.Open(newToolDocId)

            self.ts.Application.StartModification("tmp", True)
                            
            dirt =  self.ts.Documents.EnsureIsDirty(newToolDocId)

            print(f"dirt:: {dirt.PdmDocumentId} :: {newToolDocId.PdmDocumentId}")

            ops =  self.ts.Operations.GetOperations(dirt)

            print("ops", ops, len(ops))
            i = 0
           
            for o in ops:
                if i > 1:
                    break      

                Name = self.ts.Elements.GetName(o)
                #check if it's an inclusion : 3 first letters of name = "Inc"
                if Name:
                    elemType = self.get_type(o)
                    print("elemType: ", elemType)
                    if elemType == "TopSolid.Cad.Design.DB.Inclusion.InclusionOperation":
                        print("name::: ",Name)
                        print("child: ", o.DocumentId)
                        
                        IsInclusion = self.ts_d.Assemblies.IsInclusion(o)
                        print("child: ", IsInclusion, o.DocumentId)

                        if IsInclusion is True:

                            newTool = elemModelId[i]  #self.ts.Documents.GetDocument(elemModelId[i])
                            i = i + 1
                            print("newTool: ", newTool.PdmDocumentId)
                            
                            print("child: ", o.DocumentId)
                            print("child: ", newTool.PdmDocumentId)
                            
                            self.start_modif("inc", False)
                            self.ts_d.Assemblies.RedirectInclusion(o, newTool)
                            self.end_modif(True, False)
                            
            try:
                name = f"{tool.name} + {self.get_name(holder)}"
                print("*************** new assembly name: ", name)
                self.start_modif("name", False)
                self.ts.Parameters.SetTextParameterizedValue(self.ts.Elements.SearchByName(dirt, "$TopSolid.Kernel.TX.Properties.Name"), name)
                self.end_modif(True, False)
            except Exception as ex:
                print("Error setting name: ", ex)

            self.ts.Documents.Save(newToolDocId)


    def check_existing_tool(self, window, tool):        
        #check if tool is created
        if tool.TSid == "" or tool.TSid is None :
            print("INFO :: check_existing_tool :: ", tool.name," not created in ts")
            return True
        else:        
            #get the response
            box = GenericMessageBox(window, "tool already created, duplicate tool? or update TSid?", "Tool already created")
            answer = box.ShowModal()
            print("answer: ", answer)
            if answer == wx.ID_OK:
                print("duplicate tool (db and ts): ", tool.TSid)
                #duplicate tool in database and create a new tool in TS
                tool.id = 0 #set id to 0 to create a new tool
                tool.TSid = "" #set TSid to empty to create a new tool
                saveTool(tool)
                return True
            elif answer == wx.ID_YES:
                # create new tool in TS, update TSid in database and keep the same id
                print("update TSid: ", tool.TSid)
                return True
            else:
                print("canceled")
                return False
        
    def copy_tool(self, window , tool, holder, clone): #holder = true or false
        '''create a new tool in TS -> copy tool model and set tool parameters'''
        exists = self.check_existing_tool(window, tool)
        if not exists and clone is False:
            return
        else:
            #create a new tool in TS and update TSid in database
            print("INFO :: get tool TSid: ", tool.TSid)	    
            #update_tool(tool)

        #load default data
        toolDefaultData = ToolsDefaultsData()

        toolData = ToolsCustomData()
        toolData = toolData.get_custom_ts_models()

        #uncomment to prevent get TS blocked, may output an error "No modification to end."
        #EndModif(self.ts, True, False)

        try:
            #search for editool project for custom tools models and tool assembly templates
            if self.ts.IsConnected:
                output_lib = self.ts.Pdm.SearchProjectByName("editool")

                if not output_lib:
                    #if not found, use current project to create tools
                    #alert user to import/create editool library to use all features
                    print("editool library not found")
                    alert = wx.MessageBox('editool library not found, use current project to create tools', 'Warning', wx.OK | wx.ICON_QUESTION)
                    
                    #TODO :: show a dialog to create editool library
                    output_lib = self.ts.Pdm.GetCurrentProject()

                output_lib = output_lib[0]
                print("output_lib: ", output_lib.Id)
                if output_lib:
                    
                    # open it to create tool
                    self.ts.Pdm.OpenProject(output_lib)
                                    
                    # get custom tool model name
                    customToolModel = toolData.ts_models[tool.toolType]

                    # if custom model exist
                    if customToolModel:
                        print("custom model: ", customToolModel)
                        modelLib = output_lib
                        toolToCopy_ModelId = self.ts.Pdm.SearchDocumentByName(modelLib, customToolModel)
                    else:
                        print("custom model not found")
                        # or get ts default model 
                        modelLib = self.get_default_tools_lib() # TODO make it connect only one time if we create multiple tools
                        modelLib = modelLib[0]
                        tsDefaultModel = toolDefaultData.ts_models[tool.toolType]

                        print("tsDefaultModel: ", tsDefaultModel, modelLib)
                        toolToCopy_ModelId = self.ts.Pdm.SearchDocumentByName(modelLib, tsDefaultModel)
                else:
                    # if not editool project :: use current project to create tools
                    output_lib = self.ts.Pdm.GetCurrentProject()
                    print("GetCurrentProject :: ", output_lib.Id)

                print(f"*** copy tool ***  {toolDefaultData.tool_types[tool.toolType]} :: from: {self.ts.Pdm.GetName(modelLib)} :: model : {self.ts.Pdm.GetName(toolToCopy_ModelId[0])} :: to : {self.ts.Pdm.GetName(output_lib)}")
                
                #for i in toolModelId:
                #    print("toolModelId: ", i.Id)

                # need a list of PdmObjectId to CopySeveral, with only one tool model
                firstTool = toolToCopy_ModelId[0]
                toolToCopy_ModelId.Clear()
                toolToCopy_ModelId.Add(firstTool)

                #print("GetCurrentProject :: ", output_lib.Id)

                # find model tool to copy from default lib
                #print("toolModelId: ", len(toolModelId))

                savedTool = self.ts.Pdm.CopySeveral(toolToCopy_ModelId, output_lib)

                if savedTool:
                    #print(f"Tool copied successfully!  {self.ts.Pdm.GetName(savedTool[0])} ::  {savedTool[0].Id}")
                    print(f"tool model copied successfully!  {self.ts.Pdm.GetName(savedTool[0])} ::  {savedTool[0].Id}")

                savedToolDocId = self.ts.Documents.GetDocument(savedTool[0])

                #modif = self.ts.Application.StartModification("saveTool", True)
                #print("Start modif: ", modif, savedToolDocId.PdmDocumentId)
                self.start_modif("saveTool", False)
                savedToolModif = self.ts.Documents.EnsureIsDirty(savedToolDocId)

                #print("dirt savedToolModif: ", savedToolModif.PdmDocumentId)

                #Debug -> get elements param list
                """
                sys_pard = self.ts.Elements.GetElements(savedToolModif)
                print("sys_pard: ", sys_pard)
                for i in range(len(sys_pard)):
                    print("sys_pard: ", sys_pard[i])
                    print("sys_pard: ", self.ts.Elements.GetName(sys_pard[i]))            
                    if self.ts.Elements.GetName(sys_pard[i]) == "":
                        print("sys_pard: ", self.ts.Elements.GetDescription(sys_pard[i]))
                
                exit()
                """
                #get name mask
                #print("tool type: ", tool.toolType, len(toolData.tool_names_mask))
                #for mask in toolData.tool_names_mask:
                    #print("mask: ", mask)
                toolData.tool_names_mask = load_masks()
                #need to strip last char from mask _n??
                mask = toolData.tool_names_mask[tool.toolType]

                #print("mask: ", mask)

                self.ts.Parameters.SetTextParameterizedValue(self.ts.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Name"), str(mask))

                #self.ts.Parameters.SetTextParameterizedValue(self.ts.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Name"), tool.name)
                #TODO: add tool parameters config
                self.ts.Parameters.SetTextValue(self.ts.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.ManufacturerPartNumber"), str(tool.name))
                self.ts.Parameters.SetTextValue(self.ts.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Manufacturer"), str(tool.mfr))
                self.ts.Parameters.SetTextValue(self.ts.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Code"), str(tool.codeBar))
                self.ts.Parameters.SetTextValue(self.ts.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.PartNumber"), str(tool.code))
                self.ts.Parameters.SetBooleanValue(self.ts.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.VirtualDocument"), False)

                print("tool: ", tool.name, tool.mfr, tool.codeBar, tool.code)

                d1 = 0
                d2 = 0
                d3 = 0
                l1 = 0
                l2 = 0
                l3 = 0
                r = 0
                chamfer = 0
                z = 0
                threadPitch = 0.0
                threadTolerance = ""
                #print("tool type: ", tool.toolType)

                if tool.toolType == 8:#tap

                    if tool.threadTolerance and tool.threadTolerance != "None" and tool.threadTolerance != "":
                        self.ts.Parameters.SetTextValue(self.ts.Elements.SearchByName(savedToolModif,"Type"), threadTolerance)
                    else:
                        self.ts.Parameters.SetTextValue(self.ts.Elements.SearchByName(savedToolModif,"Norm"), threadTolerance)

                if tool.threadPitch and int(float(tool.threadPitch != 0)):
                    #print("thread pitch : ", tool.threadPitch)
                    threadPitch = float(tool.threadPitch / 1000).__round__(5)
                    self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"Pitch"), threadPitch)

                if tool.z:
                    z = int(float(tool.z)) #dont work with float
                    self.ts.Parameters.SetIntegerValue(self.ts.Elements.SearchByName(savedToolModif, "NoTT"), int(z))
                    #print("z: ", z)

                if tool.D1:
                    if tool.D1 is not None and tool.D1 != 0 and tool.D1 != "None": #Fix for D1 = "None"
                        d1 = float(tool.D1 / 1000).__round__(5)                
                if tool.D2: #Fix for D2 = "None"
                    if tool.D2 is not None and tool.D2 != 0 and tool.D2 != "None":
                        d2 = float(tool.D2 / 1000).__round__(5)
                else:
                    if tool.toolType == 7:
                        d2 = float(d1-threadPitch-0.2).__round__(5)
                    d2 = float(d1-(0.2/1000)).__round__(5)
                if tool.D3:
                    if tool.D3 is not None and tool.D3 != 0 and tool.D3 != "None":
                        d3 = float(tool.D3 / 1000).__round__(5)            
                if tool.L1:
                    l1 = float(tool.L1 / 1000).__round__(5) if tool.L1 is not None and tool.L1 != 0 else 0
                if tool.L2:
                    l2 = float(tool.L2 / 1000).__round__(5) if tool.L2 is not None and tool.L2 != 0 else 0
                if tool.L3:
                    l3 = float(tool.L3 / 1000).__round__(5) if tool.L3 is not None and tool.L3 != 0 else 0            
                if tool.cornerRadius:
                    #print("cornerRadius: ", tool.cornerRadius, tool.toolType  )
                    if tool.cornerRadius is not None and tool.cornerRadius != 0 and tool.cornerRadius != "None":
                        r = float(tool.cornerRadius / 1000).__round__(5)
                        if tool.toolType == 1:#radius mill
                            self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"r"), r)  
                    
                print(f" {tool.toolType} :: {d1} :  {d2} : {d3} : {l1} : {l2} : {l3} : {z}")

                #set tool parameters

                if tool.toolType == 6:#center drill
                    self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"D1"), d3)    
                    self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"D2"), d1)    
                    
                    #need to convert angle from deg to rad
                    #print("AngleDeg: ", tool.neckAngle, "chamfer: ", tool.chamfer)
                    angle = float(tool.neckAngle) * 1
                    chamfer = float(tool.chamfer) * 1

                    chamfer = float(chamfer * pi / 180).__round__(5)
                    angle = float(angle * pi / 180).__round__(5)

                    self.setRealParameter(savedToolModif,"A_T", chamfer)
                                                                        
                    self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"A"), angle)
                    #print("AngleRad: ", angle, "chamfer: ", chamfer)        
                else:
                    self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"D"), d1)                

                self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"SD"), d3)                
                self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"L"), l1)                
                self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"OL"), l3)

                print(f" {tool.toolType} :: {d1} :  {d2} : {d3} : {l1} : {l2} : {l3} : {z}")

                #if drill
                if tool.toolType == 7:#drill
                    if not tool.neckAngle:
                        tool.neckAngle = 140
                    #print("AngleDeg: ", tool.neckAngle)
                    tmpAngleRad = int(tool.neckAngle) * pi / 180
                    #print("tmpAngleRad: ", tmpAngleRad)
                    self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"A"), tmpAngleRad)
                
                #thread mill
                elif tool.toolType == 9:
                    self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"Pitch"), float(tool.threadPitch/1000).__round__(5))
                    self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"LH"), l2)
                
                    getSketchs = self.ts.Sketches2D.GetSketches(savedToolModif)
                    #print("getSketch: ", getSketchs, len(getSketchs))
                    for sketch in getSketchs:
                        sketchName = self.ts.Elements.GetName(sketch)
                        if sketchName == "ShankSketch":
                                #print("childName: ", sketchName, sketch.GetType())
                                consts = self.ts.Elements.GetConstituents(sketch)
                                #print("consts: ", consts,len(consts))
                                props = self.ts.Elements.GetProperties(sketch)
                                #print("props: ", props,len(props))

                                #for p in props:
                                    #print("prop: ",p)

                                for i in consts:
                                    constName = self.ts.Elements.GetName(i)
                                    if constName == "Dimension 3" or constName == "Dimension 4":
                                        #print("consts: ", constName, i.GetType())
                                        value = self.ts.Elements.GetTypeFullName(i)
                                        modif = self.ts.Elements.IsModifiable(i)
                                        delet = self.ts.Elements.IsDeletable(i)

                                        #print("value: ", value, modif, delet )
                                        #propType = self.ts.Elements.Delete(i)
                                        #print("propType: ", propType)
                #if spot drill
                elif tool.toolType == 6:#spot drill
                        #print("spot drill: ", l2)
                        self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"L"), l2)
                
                else:
                        
                    if l2 > 0 and tool.toolType != 8 and tool.toolType != 9 and tool.toolType != 7:
                        self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"CTS_AD"), d2)
                        self.ts.Parameters.SetRealValue(self.ts.Elements.SearchByName(savedToolModif,"CTS_AL"), l2)
                                
                from TopSolid.Kernel.Automating import SmartText

                smartTextType = SmartText(self.ts.Parameters.GetDescriptionParameter(savedToolModif))
            
                self.ts.Parameters.PublishText(savedToolModif, "FR", smartTextType)

                self.end_modif(True, False)
                
                self.ts.Documents.Save(savedToolModif)
                self.ts.Documents.Open(savedToolModif)

                #print("Created tool with id: ", savedToolModif.PdmDocumentId)
                logging.info(f"Created tool with id: {savedToolModif.PdmDocumentId}")
                tool.TSid = savedToolModif.PdmDocumentId
                
                #update tool in database
                update_tool(tool)

                if holder:
                    self.add_tool_to_holder(output_lib, tool, holder)
            
        except Exception as ex:
            self.end_modif(True, False)
            print("Error copying tool: " + str(ex))

            # Disconnect TopSolid and end the modification
            #self.ts.Disconnect()

    def setRealParameter(self, doc, paramName, value):
        #setRealParameter(savedToolModif,"A_T", chamfer)

        from TopSolid.Kernel.Automating import SmartReal
        from TopSolid.Kernel.Automating import UnitType

        SmartRealNewParam = SmartReal(UnitType(2),value) # 2 :: UnitType - Angle - 2 - Plane angle.                            

        getOps = self.ts.Operations.GetOperations (doc)
        for op in getOps:
            children = self.ts.Operations.GetChildren(op)
            for child in children:
                childName = self.ts.Elements.GetName(child)
                if childName == paramName:
                    print("childName: ", childName, child.GetType())                
                    #smartRealParam = ts_ext.Parameters.GetSmartRealParameterCreation(op) 
                    setParam = self.ts.Parameters.SetSmartRealParameterCreation(op, SmartRealNewParam)
                    print(f"set {paramName} : {SmartRealNewParam} : {value} : {setParam}")