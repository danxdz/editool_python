import winreg
import os
import clr
import wx
import logging

clr.AddReference("System.Collections")

from System.Collections.Generic import List


from step_file_viewer import StepFileViewer

from tool import Tool

key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

class use_frames:
    named_frames = []
    MCS = None
    CWS = None
    PCS = None
    WCS = None
    CSW = None

class TopSolidAPI:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        '''disconnect from TopSolid when exiting context manager and end all modifications'''
        #self.ts.Application.EndModification(True, False)
        self.end_modif(True, False)
        self.disconnect_topsolid()


    def __init__(self):
        '''initialize TopSolid API'''
        self.ts = None
        self.connected = False
        
        # to select the right tool type on import STEP file
        self.tool = None

        self._initialize_topsolid()

    def _initialize_topsolid(self):
        '''
        * ts - TopSolidHostInstance 
        * ts_d - TopSolidDesignHostInstance
        * ts_cam - TopSolidCamHostInstance
        '''

        # Get TopSolid registry key path
        key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

        try:
            # Open TopSolid registry key
            sub_keys = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            sub_keys_count = winreg.QueryInfoKey(sub_keys)[0]
            top_solid_version = winreg.EnumKey(sub_keys, sub_keys_count - 1)
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path + "\\" + top_solid_version, 0, winreg.KEY_READ)
            value = winreg.QueryValueEx(key, "InstallDir")

            top_solid_path = value[0]

            # Load TopSolid DLLs
            top_solid_kernel_sx_path = os.path.join(top_solid_path, "bin", "TopSolid.Kernel.SX.dll")
            #print(f"Loading dll: {top_solid_kernel_sx_path}")
            clr.AddReference(top_solid_kernel_sx_path)

            top_solid_kernel_path = os.path.join(top_solid_path, "bin", "TopSolid.Kernel.Automating.dll")
            #print(f"Loading dll: {top_solid_kernel_path}")
            clr.AddReference(top_solid_kernel_path)

            clr.setPreload(True)

            import TopSolid.Kernel.Automating as Automating

            self.auto = Automating
            

            top_solid_kernel_type = Automating.TopSolidHostInstance
            self.ts = clr.System.Activator.CreateInstance(top_solid_kernel_type)

            # Connect to TopSolid
            self.ts.Connect()

            if self.ts.IsConnected:
                #print only 3 first numbers of version 
                ts_version = str(self.ts.Version)[:3]
                logging.info(f"TopSolid {ts_version} connected successfully!")
                #print(f"TopSolid  {ts_version} connected successfully!") 
                #print(dir(self.ts))

                top_solid_design_path = os.path.join(top_solid_path, "bin", "TopSolid.Cad.Design.Automating.dll")
                #print(f"Loading dll: {top_solid_design_path}")
                clr.AddReference(top_solid_design_path)    
            
                #set preload to true to load all dependent dlls
                clr.setPreload(True)

                import TopSolid.Cad.Design.Automating as Automating
                self.ts_d = Automating.TopSolidDesignHostInstance(self.ts)

                # Connect to TopSolid Design
                self.ts_d.Connect()
                if self.ts_d.IsConnected:
                    self.connected = True 
                    #print(f"TopSolid Design connected successfully!")
                    #list all dll methods
                    #print(dir(self.ts_d))

                    top_solid_cam = os.path.join(top_solid_path, "bin", "TopSolid.Cam.NC.Kernel.Automating.dll")
                    #print(f"Loading dll: {top_solid_cam}")
                    clr.AddReference(top_solid_cam)    
                
                    #set preload to true to load all dependent dlls
                    clr.setPreload(True)

                    import TopSolid.Cam.NC.Kernel.Automating as Automating

                    self.ts_cam = Automating.TopSolidCamHostInstance(self.ts)

                    self.ts_cam.Connect()

                    if self.ts_cam.IsConnected:
                        #print(f"TopSolid Cam NC connected successfully! ")
                        #list all dll methods
                        #print(dir(self.ts_cam.Tools))
                        self.ts_auto = Automating
                        


        except Exception as ex:
            print("Error initializing TopSolid:", ex)
            self.connected = False

    # Get TopSolid registry key path
    def get_top_solid_path(self):
        top_solid_version = self.get_version()
        if top_solid_version is None:
            # Handle
            return None
        else:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path + "\\" + top_solid_version, 0, winreg.KEY_READ)
                value = winreg.QueryValueEx(key, "InstallDir")
                return (value[0], top_solid_version)
            except Exception as ex:
                # Handle exception
                return ex    
    

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
        # chech if connected
        if self.ts is None:
            # Handle error
            return None
        

        #PdmObjectIdType = type(self.ts.Pdm.SearchProjectByName("TopSolid Machining User Tools")) #cheat to get type
        #PdmObjectIdType = self.ts.Pdm.SearchProjectByName("TopSolid Machining User Tools")
        PdmObjectIdType = self.auto.PdmObjectId(self.ts.Pdm.SearchProjectByName("TopSolid Machining User Tools"))


        for i in PdmObjectIdType:
            name = self.ts.Pdm.GetName(i)
            #print("name: ", name)
            if name == "Outils d'usinage utilisateur TopSolid" or name == "TopSolid Machining User Tools":
                PdmObjectIdType.Clear()
                PdmObjectIdType.Add(i)
                break

        return PdmObjectIdType, name
    
    def get_language(self):
        '''get TopSolid language'''
        #string CurrentUICultureName { get; }
        return self.ts.Application.CurrentUICultureName
    

    def start_modif(self, op, ot):
        try:
            self.ts.Application.StartModification(op, ot)
            print("Start modifications")
        except Exception as ex:
            print(str(ex))
        finally:
            print("Modifications started")

    def end_modif(self, op, ot):
        try:
            self.ts.Application.EndModification(True, False)
            print("End modifications")
        except Exception as ex:
            print(str(ex))
        finally:
            print("All modifications ended")



    def get_tools(self, doc_id, used = False):
        '''get tools from tools library'''
        #toolsList<ElementId> GetTools(DocumentId inDocumentId,bool inUsed)
        tools = self.ts_cam.Documents.GetTools(doc_id, used)
        print("tools :: ", tools, len(tools))
        
        for t in tools:
            print(self.get_name(t))
            #params = self.ts_cam.Tools.GetParameters(t)
            #print("params :: ", params, len(params))
            #for p in params: 
             #   print(p)
            #List<ElementId> GetConstituents(	ElementId inElementId )


    def init_folders(self):
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

    def get_constituents(self, proj, printInfo = False):
        '''get constituents of current project'''
        if proj is None:
            proj = self.ts.Pdm.GetCurrentProject()

        proj_const = self.ts.Pdm.GetConstituents(proj)
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
                ts_type = str(self.ts.Pdm.GetType(obj)[1])
        elif obj_type is self.auto.DocumentId:
            ts_type = str(self.ts.Documents.GetType(obj)[0])
        elif obj_type is self.auto.ElementId:
            ts_type = str(self.ts.Elements.GetTypeFullName(obj))

        return ts_type

    def get_name(self, obj):
        '''get name of object by type, either PdmObjectId, DocumentId or ElementId'''
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
        current_project = self.ts.Pdm.GetCurrentProject()
        #get current project name
        current_proj_name = self.get_name(current_project)
        return current_project, current_proj_name
    
    def get_open_files(self, file_type = None):
        '''get open files'''
        docId = []
        tmp = self.ts.Documents.GetOpenDocuments()
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
    
    def is_assenbly(self, file):
        '''check if file is assembly'''
        return self.ts.Assemblies.IsAssembly(file)
    

    def open_file(self, file):
        '''open file in TopSolid'''
        try:
            #docId = self.ts_ext.Documents.GetDocument(file)
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
        #need a list of PdmObjectId
        for file in files:
            self.ts.Pdm.CheckIn(file, True)


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
                if tmp.Count > 1:
                    for i in tmp:
                        docId.append(i)
                    return docId
                else:
                    return tmp
            
            #print(f"file opened : {docId}")
        except Exception as ex:
            print(str(ex))
        finally:
            print(f"number of open files : {num}")
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

        if name == "MCS":
            use_frames.MCS = frame
        elif name == "CWS":
            use_frames.CWS = frame
        elif name == "PCS":
            use_frames.PCS = frame
        elif name == "WCS" or name == "$TopSolid.Kernel.DB.D3.Documents.ElementName.AbsoluteFrame":
            use_frames.WCS = frame
        elif name == "CSW":
            use_frames.CSW = frame

        use_frames.named_frames.append(name)
        
    def change_option(self, opt, key, value):
        '''change option in importer options'''
        if opt.Key == key:
            opt.Value = value
            # debug options values
            #print(f"option {key} changed to {value}")
        return opt
    
    def get_importer_options(self, inImporterIx): #inImporterIx = type of file to import #10 for .step file
        '''get file importer options'''
        
        opt = self.ts.Application.GetImporterOptions(inImporterIx)
        # debug importer options
        #print("opt :: ", opt, len(opt))

        # Create a copy of the list by iterating over it
        opt_copy = [item for item in opt]

        for i, item in enumerate(opt_copy):
            if item.Key == "SIMPLIFIES_GEOMETRY" or item.Key == "SEWS_SHEETS": # add more options to change if needed
                opt[i] = self.change_option(item, item.Key, "True")
            else:
                opt[i] = self.change_option(item, item.Key, item.Value)
        return opt
                

    def exec_import(self, inImporterIx, inFullName, inOwnerId):  
        '''execute import with options'''

        uop = ""
        out = ""

        file_type = self.ts.Application.GetImporterFileType(inImporterIx, uop, out) #inImporterIx = type of file to import
        print(f"file type to import :: {file_type} :: {inImporterIx} :: {uop} :: {out}")

        set_opt = self.get_importer_options(inImporterIx)
                        
        result = self.ts.Documents.ImportWithOptions(inImporterIx, set_opt ,  inFullName,  inOwnerId)

        print(f"Import result: {len(result)}")

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



    def Import_file_w_conv(self, inImporterIx, inFullName, inOwnerId):
        '''import file with conversion'''

        print("INFO :: import file with conversion :: ", inImporterIx, inFullName)
        
        outLog = []
        outBadDocumentIds = [self.auto.DocumentId]

        try:            
            step_viewer = StepFileViewer()
            # load the step file
            print("INFO :: file loaded :: ", inFullName)
            step_viewer.loadStepFile(inFullName)

            # AXIS2_PLACEMENT_3D names to search for
            holder_placement_names = ['MCS', 'CWS', 'PCS', 'WCS', 'CSW']
            tool_placement_names = ['MCS', 'CWS', 'PCS', 'WCS', 'CSW',"CIP","CIP_SCHNEIDE"]

            found_elements = step_viewer.findPlacementElements()

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

            frames = self.get_Frames(newdoc[0])                            

            #open the file
            print("get_Frames :: ", len(frames))

            self.open_file(newdoc[0])
                        
            self.start_modif("frame", False)

            if len(frames) :#<= 1:
                
                # Get the absolute frame of the document #ElementId GetAbsoluteFrame(DocumentId inDocumentId)
                abs_smartFrame = self.ts.Geometries3D.GetAbsoluteFrame(newdoc[0])

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
                        
                        sdir = self.auto.SmartDirection3D(direction_z, p3d)
                        
                        #ItemLabel(byte inType,int inId,string inMoniker,string inName)
                        label = self.auto.ItemLabel(0, 0, f"{name}_tip", f"{name}_tip")

                        #need to calculate the the direction_y
                        #public static Vector3D operator ^(Direction3D inDirection1,Direction3D inDirection2)
                        vector_y = (direction_z  ^ direction_x)

                        #vector 2 direction
                        #public static explicit operator Direction3D (Vector3D inVector)
                        direction_y = self.auto.Direction3D(vector_y.X, vector_y.Y, vector_y.Z)


                        #create a new frame with the same name if not exists
                        if name == "CIP" or name == "CIP_SCHNEIDE":
                            # inverted -direction_y and direction_z to get the right orientation
                            # Frame3D Frame3D(Point3D inOrigin,Direction3D inXDirection,Direction3D inZDirection,Direction3D inYDirection)
                            new_frame = self.auto.Frame3D(p3d, direction_x,  direction_z, -direction_y)     
                        else:
                            # to create the frame as the same orientation as the step file
                            new_frame = self.auto.Frame3D(p3d, direction_x,  direction_y, direction_z) 

                        created_frame = self.ts.Geometries3D.CreateFrame(newdoc[0], new_frame)
                        # SetName(ElementId inElementId,string inName)
                        f_name = self.ts.Elements.GetFriendlyName(created_frame)
                        print("f_name :: ", f_name, name)
                        self.ts.Elements.SetName(created_frame, f"{name}_tip")
                        self.setFrame(created_frame)
                              

                # Read shapes in the file
                    
                #List<ElementId> GetShapes(DocumentId inDocumentId)                    
                shapes = self.ts.Shapes.GetShapes(newdoc[0])
                print("***************************************************************")
                print("shapes :: ", shapes, len(shapes))
                if len(shapes) > 1:
                    for shape in shapes:
                        shape_name = self.get_name(shape)
                        shape_type = self.get_type(shape)
                        print(shape_name, shape_type, self.ts.Shapes.GetShapeType(shape))
                        
                        if str(shape_name) == "CUT":
                            self.tool = True
                            tool = Tool()
                            print("INFO :: n of faces :: ", self.ts.Shapes.GetFaceCount(shape))

                            faces = self.ts.Shapes.GetFaces(shape)
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
                                print("edges :: ", edges, len(edges))
                                for edge in edges:
                                    # CurveType GetEdgeCurveType(ElementItemId inEdgeId)
                                    c_type = self.ts.Shapes.GetEdgeCurveType(edge)
                                    print(edge, c_type )
                                    if str(c_type) == "Circle":
                                        # void GetEdgeCircleCurve(ElementItemId inEdgeId,out Plane3D outPlane,out double outRadius)
                                        circle , c_radius = self.ts.Shapes.GetEdgeCircleCurve(edge)
                                        print("circle :: ", circle, c_radius)
                                        tool.D1 = c_radius * 2 * 1000

                                '''
                                #Function GetFaceSurfaceParameters ( 
                                                inFaceId As ElementItemId,
                                                inPoint As Point3D,
                                                <OutAttribute> ByRef outU As Double,
                                                <OutAttribute> ByRef outV As Double
                                            ) As Point3D

                                            Dim instance As IShapes
                                            Dim inFaceId As ElementItemId
                                            Dim inPoint As Point3D
                                            Dim outU As Double
                                            Dim outV As Double
                                            Dim returnValue As Point3D

                                            returnValue = instance.GetFaceSurfaceParameters(inFaceId, 
                                                inPoint, outU, outV)
                                                '''
                                outU = 0.0
                                outV = 0.0


                                if str(face_type) == "Cylinder":
                                    '''void GetFaceRange(
                                                            ElementItemId inFaceId,
                                                            out double outUMin,
                                                            out double outUMax,
                                                            out double outVMin,
                                                            out double outVMax)
                                                        '''
                                    


                                    for cf in connected_faces:                                        
                                        cf_type = self.ts.Shapes.GetFaceSurfaceType(cf)
                                        print(cf_type)

                                        #void GetFaceCylinderSurface(ElementItemId inFaceId,out Frame3D outFrame,out double outRadius)
                                        if str(cf_type) == "Cylinder":
                                            print(cf)

                                            cyl_face = self.ts.Shapes.GetFaceCylinderSurface(face)
                                            print("cyl_face :: ", cyl_face)
                                            for c in cyl_face:
                                                print(c)
                                                #double GetFaceCylinderRadius(ElementItemId inFaceId)
                                                #diam = self.ts.Shapes.GetFaceCylinderRadius(c)
                                                #print("diam :: ", diam)



                                x_min = 0.0
                                x_max = 0
                                y_min = 0
                                y_max = 0
                                z_min = 0
                                z_max = 0

                            '''
                                self.ts.Shapes.GetFaceEnclosingCoordinates(face, x_min, x_max, y_min, y_max, z_min, z_max)
                                print(f"face {face} :: {x_min} :: {x_max} :: {y_min} :: {y_max} :: {z_min} :: {z_max}")'''
                            

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

                            eii = self.auto.ElementItemId(shape, self.auto.ItemLabel(0, 0, "CUT", "CUT"))

                            print("eii :: ", eii)

                            
                            print("Multiple shapes found, and 'CUT' shape, is a tool :: D1 :: ", tool.D1)
                            
                    if self.tool == False:
                        print("Multiple shapes found, no 'CUT' shape, is a holder")
                
                else:
                    print("One shape found, no tool found, is a holder")
                    self.tool = False

                #**************************************************************
                # need to check if is a tool or holder before begin the process
                #**************************************************************
                # if tool need 2 shapes, so 2 revolved sketches
                # if holder need 1 shape, so 1 revolved sketch

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
                newAxis = self.auto.SmartAxis3D(axis[2],  False)

                #print("newAxis :: ", newAxis, self.get_name(newAxis))

                #get the shape to revolve
                for shape in shapes:
                    shape = self.auto.SmartShape(shape)
                    #print("shape :: ", shape, self.get_name(shapes[0]))

                    planes = self.ts.Geometries3D.GetPlanes(newdoc[0])
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
            
            if self.tool == True:
                print("INFO :: add tool functions")
                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Fraise 2 tailles")
                print("ts_func :: ", ts_func, len(ts_func), self.get_name(ts_func[0]))
                func_doc = self.ts.Documents.GetDocument(ts_func[0])
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Fraise 2 tailles")     

            else: 
                print("INFO :: add holder functions")
                #get function PdmDocumentId by Name
                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Attachement cylindrique porte outil")              
                print("ts_func :: ", ts_func, len(ts_func), self.get_name(ts_func[0]))
                #Get DocumentId by PdmObjectId
                func_doc = self.ts.Documents.GetDocument(ts_func[0])         
                #ElementId ProvideFunction( DocumentId inDocumentId,DocumentId inFunctionId,string inOccurrenceName)                
               
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Attachement cylindrique porte outil")
                #prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Attachement cylindrique pour l'outil")

                # IGeometries3D - void SetFramePublishingDefinition( inElementId,SmartFrame3D inDefinition)
                        #self.design.Geometries3D.SetFramePublishingDefinition(prov_func, use_frames.CSW)
                
                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Profil de révolution pour l'analyse de collision")
                print("ts_func :: ", ts_func, len(ts_func))
                func_doc = self.ts.Documents.GetDocument(ts_func[0])
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Profil def collision")
                
                ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Système de fixation outil")
                print("ts_func :: ", ts_func, len(ts_func))
                func_doc = self.ts.Documents.GetDocument(ts_func[0])
                #prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Système de fixation vers la machine")
                prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Système de fixation outil")
                
                #List<ElementId> GetFunctions( DocumentId inDocumentId )                
                functions = self.ts.Entities.GetFunctions(newdoc[0])


                
                print("functions :: ", functions, len(functions))
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

                    #self.start_modif("func", False)

                    for pub in func_pubs:
                        print("INFO :: function found :: ", self.get_name(pub), self.get_type(pub))
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
                            self.ts.Geometries3D.SetFramePublishingDefinition(pub, use_frames.PCS)
                        elif self.get_name(pub) == "ToolingSystemName":
                            pub_type = self.get_type(pub)
                            #print("pub_type :: ", pub_type)
                            if pub_type == "TopSolid.Kernel.DB.D3.Frames.PublishingFrameEntity":
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
                            sketches = self.ts.Sketches2D.GetSketches(newdoc[0])
                            #print("sketches :: ", self.get_name(sketches[0]), len(sketches))
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
            # Trate a exceção conforme necessário
            print(f"Error importing documents: {e}")
            self.end_modif(True, False)
            raise




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


    def searchHolder(self, file):
        '''search holder in file'''
        holder_found = 0
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
                                if function.startswith("Tooling Shank") or function.startswith("Attachement cylindrique porte outil") or function.startswith("Système de fixation porte-outil") or function.startswith("Attachement cylindrique pour l'outil") or function.startswith("Attachement cylindrique porte outil  <ToolingHolder_1>"):
                                    print(f"found : {function}")
                                    holder_found += 1
                                    #create_tool_w_holder(api.ts ,api.ts_d , output_lib, tool, holder)
                                    break
                                elif function == "Compensation outil <TO>":
                                    print(f"not an holder : {function} is one tool")
                                    break
        return holder_found

    def insert_into_holder(self, tool):
        '''insert tool into holder'''        
        try:
            proj = self.get_current_project()
            #get open files
            open_files = self.get_open_files()
            print("current project :: ", proj[1] , len(open_files))

            if len(open_files) == 0:
                #msg box theres no open holder in TS
                output_msg = wx.MessageBox('no files open on TS, try to open an holder and retry', 'Warning', wx.OK | wx.CANCEL | wx.ICON_QUESTION)                      
            
            #check if any holder is open in TS
            holder_found = self.searchHolder(open_files)
            
            if holder_found == 0:
                noTool = wx.MessageBox('holder not open on TS, try to open and retry', 'Warning', wx.OK |wx .CANCEL | wx.ICON_QUESTION)
                if noTool == wx.OK:
                    self.copy_holder(self, tool)
                print("noTool: ", noTool)                 

        except Exception as ex:
            # msg box error copying tool
            dialog = wx.MessageBox('Error copying tool: ' + str(ex), 'Warning', wx.OK_DEFAULT | wx.ICON_ERROR)

            print("Error copying tool: " + str(ex))
            self.end_modif(True, False)

        return False
