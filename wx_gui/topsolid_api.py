import winreg
import os
import clr
import re
clr.AddReference("System.Collections")
from System.Collections.Generic import List


import wx

from step_file_viewer import StepFileViewer


key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

class use_frames:
    MCS = None
    CWS = None
    PCS = None
    WCS = None
    CSW = None

class TopSolidAPI:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect_topsolid()

    def __init__(self):
        self.ts = None
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

            top_solid_kernel_type = Automating.TopSolidHostInstance
            self.ts = clr.System.Activator.CreateInstance(top_solid_kernel_type)

            # Connect to TopSolid
            self.ts.Connect()

            if self.ts.IsConnected:
                #print only 3 first numbers of version 
                ts_version = str(self.ts.Version)[:3]
                print(f"TopSolid  {ts_version} connected successfully!") 
                #print(dir(self.ts))
                self.connected = True 

                top_solid_design_path = os.path.join(top_solid_path, "bin", "TopSolid.Cad.Design.Automating.dll")
                print(f"Loading dll: {top_solid_design_path}")
                clr.AddReference(top_solid_design_path)    
            
                #set preload to true to load all dependent dlls
                clr.setPreload(True)
                import TopSolid.Cad.Design.Automating as Automating
                self.ts_d = Automating.TopSolidDesignHostInstance(self.ts)

                # Connect to TopSolid Design
                self.ts_d.Connect()
                if self.ts_d.IsConnected:
                    print(f"TopSolid Design connected successfully!")
                    #list all dll methods
                    #print(dir(self.ts_d))
                    print("TopSolid Design version: ", self.ts_d.ToString()) 

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

    def get_ts_design_ext(self):
        ts = self.get_top_solid_path()
        top_solid_path = ts[0]
        if top_solid_path is None:
            # Handle
            return None

        top_solid_design_path = os.path.join(
        top_solid_path, "bin", "TopSolid.Cad.Design.Automating.dll")
        print(f"Loading dll: {top_solid_design_path}")
        clr.AddReference(top_solid_design_path)    
        
        #set preload to true to load all dependent dlls
        clr.setPreload(True)

        import TopSolid.Cad.Design.Automating as Automating

        return Automating
    
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
        # Load TopSolid DLLs
        if self.ts is None:
            # Handle error
            return None

        PdmObjectIdType = type(self.ts.Pdm.SearchProjectByName("TopSolid Machining User Tools")) #cheat to get type
        PdmObjectIdType = self.ts.Pdm.SearchProjectByName("TopSolid Machining User Tools")


        for i in PdmObjectIdType:
            name = self.ts.Pdm.GetName(i)
            #print("name: ", name)
            if name == "Outils d'usinage utilisateur TopSolid" or name == "TopSolid Machining User Tools":
                PdmObjectIdType.Clear()
                PdmObjectIdType.Add(i)
                break

        return PdmObjectIdType, name
    

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
            raw_ts_type = self.ts.Pdm.GetType(obj)
            if str(raw_ts_type[0]) == "Folder":
                ts_type = str(raw_ts_type[0])
            else:
                ts_type = str(self.ts.Pdm.GetType(obj)[1])
        elif obj_type is DocumentId:
            is_part = self.ts.Documents.IsPart(obj)
            ts_type = str(self.ts.Documents.GetType(obj)[0])
        elif obj_type is ElementId:
            ts_type = str(self.ts.Elements.GetTypeFullName(obj))

        return ts_type

    def get_name(self, obj):
        '''get name of object by type, either PdmObjectId, DocumentId or ElementId'''
        obj_type = type(obj)
        name = ""
    
        from TopSolid.Kernel.Automating import PdmObjectId
        from TopSolid.Kernel.Automating import DocumentId
        from TopSolid.Kernel.Automating import ElementId

        if obj_type is PdmObjectId:
            name = str(self.ts.Pdm.GetName(obj))
        elif obj_type is DocumentId:
            name = str(self.ts.Documents.GetName(obj))
        elif obj_type is ElementId:
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
            self.ts.Documents.Open(file)
            print("file opened")
        except Exception as ex:
            print(str(ex))
        finally:
            print("All modifications ended")

    def check_in(self, file):
        '''check in file'''
        from TopSolid.Kernel.Automating import PdmObjectId
        #PdmObjectId GetPdmObject( DocumentId inDocumentId )
        pdm_obj = self.ts.Documents.GetPdmObject(file)
        print("file to check in :: ", file.PdmDocumentId)
        self.ts.Pdm.CheckIn(pdm_obj, True)

    def check_in_all(self, files):
        '''check in all files in list'''
        from TopSolid.Kernel.Automating import PdmObjectId
        #need a list of PdmObjectId
        for file in files:
            self.ts.Pdm.CheckIn(file, True)


    def ask_plan(self, file):

        from TopSolid.Kernel.Automating import UserQuestion

       

        '''ask repere of file'''
        try:
           
            titre = "Plan XY"
            label = "Merci de sélectionner le plan XY du repère"
            QuestionPlan = UserQuestion(titre, label)
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
        print("INFO :: frames :: ", frames, len(frames))
        return frames
    
    def setFrame (self, frame):
        #ItemLabel(byte inType,int inId,string inMoniker,string inName)
        from TopSolid.Kernel.Automating import ItemLabel
        from TopSolid.Kernel.Automating import SmartFrame3D

        name = self.get_name(frame)
        
        frame = SmartFrame3D(frame, False)
        print("setFrame :: ", name)

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

        

    def Import_file_w_conv(self, inImporterIx, inFullName, inOwnerId):
        try:            
            step_viewer = StepFileViewer()
            # load the step file
            print("Loading step file")
            step_viewer.loadStepFile(inFullName)

            # AXIS2_PLACEMENT_3D names to search for
            placement_names = ['MCS', 'CWS', 'PCS', 'WCS', 'CSW']

            found_elements = step_viewer.findPlacementElements(placement_names)

            print("Found elements:")
            print(found_elements)  
        
            from TopSolid.Kernel.Automating import DocumentId
            from TopSolid.Kernel.Automating import KeyValue            
            from TopSolid.Kernel.Automating import SmartFrame3D

            outLog = []
            outBadDocumentIds = [DocumentId]

            ''' debug
            for i in range(0, 100):
                file_type = self.design.Application.GetImporterFileType(i, uop, out)
                
                string_array = file_type[1]

                # Converting each element of the array to string and storing them in a list
                string_list = [str(x) for x in string_array]

                # Now you can access the text as strings in the string_list
                print(f"{i} :: {file_type[0]} : {string_list}")

                opt = self.design.Application.GetImporterOptions(importer_type)
                for i, item in enumerate(opt):
                    print(f"    - {i} :: {item.Key} : {item.Value}")
            exit()'''

            uop = ""
            out = ""

            file_type = self.ts.Application.GetImporterFileType(inImporterIx, uop, out)
            print("file_type :: ", file_type, uop, out)        

            opt = self.ts.Application.GetImporterOptions(inImporterIx)
            print("opt :: ", opt, len(opt)) 
            
            # need to change 'SIMPLIFIES_GEOMETRY' to True
            # but is index change from TS version to version, so lets loop through the options and change the one we want
            for i, item in enumerate(opt):
                print(i, item.Key, item.Value)
                if item.Key == "SIMPLIFIES_GEOMETRY":
                    opt[i] = KeyValue("SIMPLIFIES_GEOMETRY", "True")
                    opt[i+1] = KeyValue("SEWS_SHEETS", "True") 
                    opt[i+2] = KeyValue("LINEAR_TOLERANCE", "1E-01") # 1E-05 = 0.00001 / 1E-01 = 0.1
                    opt[12] = KeyValue("DEEP_HEALING", "True")
                    print("SIMPLIFIES_GEOMETRY changed to True")
                    break

            ''' Default options 716
            0 TRANSLATES_ASSEMBLY True
            1 TRANSLATES_ATTRIBUTES True
            2 SIMPLIFIES_GEOMETRY True
            3 SEWS_SHEETS True
            4 LINEAR_TOLERANCE 1E-02 # 1E-05 = 0.00001 / 1E-01 = 0.1 / 1E-02 = 0.01 
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

            for i, item in enumerate(opt):
                print(i, item.Key, item.Value)
                            
            result = self.ts.Documents.ImportWithOptions(inImporterIx, opt ,  inFullName,  inOwnerId)

            print(f"Import result: {result}")

            newdoc = result[0]

            # ************************************************************************************************
            # ************************************************************************************************
            # ************************************************************************************************
            # Process the found elements after the import

            frames = self.get_Frames(newdoc[0])
            for frame in frames:
                self.setFrame(frame)
                

            #open the file
            print("Opening file", len(newdoc))

            self.open_file(newdoc[0])
            

            if len(frames) :#<= 1:

                #IGeometries3D.CreateSmartFrame 
                #ElementId CreateSmartFrame(DocumentId inDocumentId,SmartFrame3D inProvidedSmartFrame)
                #SmartFrame3D(SmartFrame3D inReferenceFrame,SmartDirection3D inDirection,SmartReal inDistance
                    
                #Public Sub New ( inReferenceFrame As SmartFrame3D,inDirection As SmartDirection3D,inDistance As SmartReal)
                    
                #Dim instance As New SmartFrame3D(inReferenceFrame, inDirection, inDistance)
                    
                                
                from TopSolid.Kernel.Automating import SmartDirection3D
                from TopSolid.Kernel.Automating import SmartReal
                from TopSolid.Kernel.Automating import SmartAxis3D
                from TopSolid.Kernel.Automating import SmartShape
                from TopSolid.Kernel.Automating import Direction3D
                from TopSolid.Kernel.Automating import UnitType
                from TopSolid.Kernel.Automating import SmartDirection3D
                from TopSolid.Kernel.Automating import Point3D
                from TopSolid.Kernel.Automating import SmartPoint3D
                from TopSolid.Kernel.Automating import ItemLabel
                from TopSolid.Kernel.Automating import Point2D
                from TopSolid.Kernel.Automating import SmartPoint2D 
                from TopSolid.Kernel.Automating import Direction2D
                from TopSolid.Kernel.Automating import SmartDirection2D
                from TopSolid.Kernel.Automating import Plane3D
                from TopSolid.Kernel.Automating import SmartPlane3D
                from TopSolid.Kernel.Automating import SmartText
                from TopSolid.Kernel.Automating import SmartSection3D
                from TopSolid.Kernel.Automating import Frame3D
                from TopSolid.Kernel.Automating import SmartFrame3DType

                inReferenceFrame = frames[0]

                Main_SmartFrame = SmartFrame3D( inReferenceFrame, False )
                print("newSmartFrame :: ", Main_SmartFrame)

                for name, placement in found_elements.items():
                    print(f"Found {name} :: {placement.name} : {placement.coord} : {placement.dir1} : {placement.dir2}") 

                    direction = Direction3D(placement.dir1.x, placement.dir1.y, placement.dir1.z)
                    print("direction :: ", direction)
                    dif = placement.coord.z
                    distance = SmartReal(UnitType.Length, (dif/1000)) #3 = length unit, 0.001 = 1mm                    

                    print("distance :: ", distance)
                    p3d = Point3D(placement.coord.x, placement.coord.y, placement.coord.z)
                    sdir = SmartDirection3D(direction, p3d)

                    
                    label = ItemLabel(0, 0, name, name)

                    test = Frame3D(p3d, Direction3D(1, 0, 0), Direction3D(0, 1, 0), Direction3D(0, 0, 1))
                    # ElementId CreateFrame(DocumentId inDocumentId,Frame3D inGeometry)

                    self.start_modif("frame", False)

                    new_frame = self.ts.Geometries3D.CreateFrame(newdoc[0], test)

                    print("00new_frame :: ", new_frame, self.get_name(new_frame))

                    # SetName(ElementId inElementId,string inName)

                    f_name = self.ts.Elements.GetFriendlyName(new_frame)

                    print("f_name :: ", f_name, name)
                    if name:
                        self.ts.Elements.SetName(new_frame, name)
                        self.setFrame(new_frame)

                


                    '''
                    public SmartFrame3D(
                                        SmartFrame3DType inType,
                                        Nullable<Frame3D> inGeometry,
                                        Nullable<double> inExtentXMin,
                                        Nullable<double> inExtentXMax,
                                        Nullable<double> inExtentYMin,
                                        Nullable<double> inExtentYMax,
                                        Nullable<double> inExtentZMin,
                                        Nullable<double> inExtentZMax,
                                        ElementId inElementId,
                                        ItemLabel inItemLabel,
                                        bool inIsReversed
                    )
                    '''

                    #public enum SmartFrame3DType

                    new_frame = SmartFrame3D(SmartFrame3DType(4), test, 0, 0, 0, 0, 0, 0, frames[0], label, False)

                    named_frame = SmartFrame3D(new_frame.ElementId , label, False)


                    print("new_frame :: ", new_frame.Type, named_frame.Type)
                          
                    #start_modif


                    new_frame = self.ts.Geometries3D.CreateSmartFrame(newdoc[0],  new_frame) 
                    print("new_frame :: ", new_frame)
                    
                #List<ElementId> GetShapes(DocumentId inDocumentId)
                shapes = self.ts.Shapes.GetShapes(newdoc[0])
                print("shapes :: ", shapes, len(shapes))
                for shape in shapes:
                    print(self.get_name(shape), self.get_type(shape))

                axis = self.ts.Geometries3D.GetAxes(newdoc[0])
                print("axis :: ", axis)
                for ax in axis:
                    print(self.get_name(ax))

                newAxis = SmartAxis3D(axis[2],  False)
                print("newAxis :: ", newAxis, self.get_name(newAxis))

                #ElementId CreateRevolvedSilhouette(SmartShape inShape,SmartAxis3D inAxis,bool inMerge)

                shape = SmartShape(shapes[0])
                print("shape :: ", shape, self.get_name(shape))

                planes = self.ts.Geometries3D.GetPlanes(newdoc[0])
                for plane3d in planes:
                    print(self.get_name(plane3d))

                # SmartPlane3D(planes[0], False)
                #plane = Plane3D(p3d, Direction3D(1, 0, 0), Direction3D(0, 0, 1))
                #splane = SmartPlane3D(plane, 0,0,0,0)

                plane = self.ts.Geometries3D.GetAbsoluteXZPlane(newdoc[0])
                splane = SmartPlane3D(plane, False)


                sketch = self.ts.Sketches2D.CreateSketchIn3D(newdoc[0], splane,  SmartPoint3D(Point3D(0, 0, 1)), True, SmartDirection3D(Direction3D(1, 0,0), Point3D(1, 0, 0)))



                self.ts.Sketches2D.StartModification(sketch)
                revolv = self.ts.Sketches2D.CreateRevolvedSilhouette(shape, newAxis, True)
                self.ts.Sketches2D.EndModification()

        
            

            #SearchProjectByName(string inProjectName)
            func_proj =  self.ts.Pdm.SearchProjectByName("TopSolid Machining")
            print("func_proj :: ", func_proj, len(func_proj))

            for func in func_proj:
                print(self.get_name(func), self.get_type(func))
                if self.get_name(func) == "Usinage TopSolid" or self.get_name(func) == "TopSolid Machining":
                    func_proj = func
                    break
            
            
            #get function PdmDocumentId by Name
            ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Attachement cylindrique porte outil")              
            print("ts_func :: ", ts_func, len(ts_func), self.get_name(ts_func[0]))
            #Get DocumentId by PdmObjectId
            func_doc = self.ts.Documents.GetDocument(ts_func[0])         
            #ElementId ProvideFunction( DocumentId inDocumentId,DocumentId inFunctionId,string inOccurrenceName)                
            prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Attachement cylindrique pour l'outil")

            # IGeometries3D - void SetFramePublishingDefinition( inElementId,SmartFrame3D inDefinition)
                    #self.design.Geometries3D.SetFramePublishingDefinition(prov_func, use_frames.CSW)


            
            ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Profil de révolution pour l'analyse de collision")
            print("ts_func :: ", ts_func, len(ts_func))
            func_doc = self.ts.Documents.GetDocument(ts_func[0])
            prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Profil def collision")
            
            ts_func = self.ts.Pdm.SearchDocumentByName(func_proj, "Système de fixation outil")
            print("ts_func :: ", ts_func, len(ts_func))
            func_doc = self.ts.Documents.GetDocument(ts_func[0])
            prov_func = self.ts.Entities.ProvideFunction(newdoc[0], func_doc, "Système de fixation vers la machine")
            
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



                self.start_modif("func", False)

                for pub in func_pubs:
                    print(self.get_name(pub))

                    '''
                    ToolingSystemFrame
                    ToolingSystemName
                    ToolingSystemSize
                    '''

                    if self.get_name(pub) == "ToolingSystemFrame":
                        #SetFramePublishingDefinition( inElementId,SmartFrame3D inDefinition)
                        self.ts.Geometries3D.SetFramePublishingDefinition(pub, use_frames.PCS)
                        print("pub :: ", pub, self.get_name(pub))
                    elif self.get_name(pub) == "ToolingSystemName":
                        pub_type = self.get_type(pub)
                        print("pub_type :: ", pub_type)
                        if pub_type == "TopSolid.Kernel.DB.D3.Frames.PublishingFrameEntity":
                            self.ts.Geometries3D.SetFramePublishingDefinition(pub, use_frames.CSW)
                        else:
                            #IParameters.SetTextPublishingDefinition Method  
                            pub_name = SmartText("HSK")
                            self.ts.Parameters.SetTextPublishingDefinition(pub, pub_name)
                        print("pub :: ", pub, self.get_name(pub))
                    elif self.get_name(pub) == "ToolingSystemSize":
                        pub_size = SmartReal(UnitType.Length, (63/1000)) 
                        #IParameters.SetTextPublishingDefinition Method
                        self.ts.Parameters.SetRealPublishingDefinition(pub, pub_size)
                        print("pub :: ", pub, self.get_name(pub))
                    elif self.get_name(pub) == "ToolingSystemType":
                        pub_name = SmartText("Mandrin pour queue cylindrique")
                        self.ts.Parameters.SetTextPublishingDefinition(pub, pub_name)
                        print("pub :: ", pub, self.get_name(pub))
                    elif self.get_name(pub) == "Revolute Section":
                        #List<ElementId> GetSketches( DocumentId inDocumentId )
                        sketches = self.ts.Sketches2D.GetSketches(newdoc[0])
                        print("sketches :: ", self.get_name(sketches[0]), len(sketches))
                        #public SmartSection3D(ElementId inElementId)
                        sect = SmartSection3D(sketches[0])
                        print("sect :: ", sect, self.get_name(sect))
                        #void SetSectionPublishingDefinition(ElementId inElementId,SmartSection3D inDefinition)
                        self.ts.Geometries3D.SetSectionPublishingDefinition(pub, sect)


                #print("revolv :: ", revolv)

                out = ""
                print("new_frame :: ", new_frame)


            

            smartTextType = SmartText(self.ts.Parameters.GetDescriptionParameter(newdoc[0]))

            self.ts.Parameters.PublishText(newdoc[0], "PO", smartTextType)


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


    