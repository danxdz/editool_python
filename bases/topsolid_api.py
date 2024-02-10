import winreg
import os
import clr
import re
clr.AddReference("System.Collections")
from System.Collections.Generic import List


import wx

class use_frames:
    MCS = None
    CWS = None
    PCS = None
    WCS = None
    CSW = None



class CartesianPoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        return self.__str__()

class Direction:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        return self.__str__()

class Axis2Placement3D:
    def __init__(self, name, coord, dir1, dir2):
        self.name = name
        self.coord = coord
        self.dir1 = dir1
        self.dir2 = dir2
    
    def __str__(self):
        return f"{self.name}: coord={self.coord}, dir1={self.dir1}, dir2={self.dir2}"
    
    def __repr__(self):
        return self.__str__()

    

class StepFileViewer:
    def __init__(self):
        self.step_data = None

    def loadStepFile(self, step_file_path):
        try:
            with open(step_file_path, 'r') as step_file:
                self.step_data = step_file.readlines()

        except Exception as e:
            print(f"Error loading STEP file: {e}")
            raise

    def findPlacementElements(self, element_names):
        found_elements = {}

        if self.step_data is None:
            print("Step data not loaded. Call loadStepFile() first.")
            return found_elements

        for line in self.step_data:
            if line.startswith("#"):
                # #1661=AXIS2_PLACEMENT_3D('MCS',#1658,#1659,#1660);
                # Break down the line into its parts
                parts = re.split(r'[(),]', line)
                try:
                    # Get the element number
                    num = parts[0].replace("#", "")
                    element_number = num.split("=")[0]
                    element_type = num.split("=")[1]

                    # Check if the element type is AXIS2_PLACEMENT_3D:
                    if element_type == "AXIS2_PLACEMENT_3D":
                        # Get the element name
                        element_name = parts[1].replace("'", "")

                        # Get the element content
                        element_content = parts[2:]

                        # If element has a name
                        if True:#element_name:# and element_name in element_names:
                            cart = element_content[0].replace("#", "")
                            dir1 = element_content[1].replace("#", "")
                            dir2 = element_content[2].replace("#", "")

                            cart_content = self.get_element_content(cart)
                            dir1_content = self.get_element_content(dir1)
                            dir2_content = self.get_element_content(dir2)

                            coord = CartesianPoint(float(cart_content[0]), float(cart_content[1]), float(cart_content[2]))
                            dir1 = Direction(float(dir1_content[0]), float(dir1_content[1]), float(dir1_content[2]))
                            dir2 = Direction(float(dir2_content[0]), float(dir2_content[1]), float(dir2_content[2]))

                            axis_placement = Axis2Placement3D(element_name, coord, dir1, dir2)
                            found_elements[element_name] = axis_placement

                except Exception as e:
                    print(f"Error parsing element content: {e}")

        return found_elements

    def get_element_content(self, element_number):
        content = []
        for line in self.step_data:
            if line.startswith(f"#{element_number}"):
                parts = re.split(r'[(),]', line)
                try:
                    x = parts[3].replace("'", "")
                    y = parts[4].replace("'", "")
                    z = parts[5].replace("'", "")
                    content = [x, y, z]
                except Exception as e:
                    print(f"Error parsing element content: {e}")
        return content



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
            self.design.Application.EndModification(True, False)
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

    def check_in(self, file):
        '''check in file'''
        from TopSolid.Kernel.Automating import PdmObjectId
        #PdmObjectId GetPdmObject( DocumentId inDocumentId )
        pdm_obj = self.design.Documents.GetPdmObject(file)
        print("file to check in :: ", file.PdmDocumentId)
        self.design.Pdm.CheckIn(pdm_obj, True)

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

    def ImportFile(self, inFullName, inOwnerId, inDocumentName):
            try:
                
                # Substitua essas linhas pela chamada real do método ImportFile na sua interface
                result = self.design.Pdm.ImportFile(inFullName, inOwnerId, inDocumentName)
                return result
            except Exception as e:
                # Trate a exceção conforme necessário
                print(f"Error importing file: {e}")
                raise


    def Import_file_w_conv(self, inImporterIx, inFullName, inOwnerId):
        try:

            
            step_viewer = StepFileViewer()
            # load the step file
            print("Loading step file")
            step_viewer.loadStepFile(inFullName)

            # AXIS2_PLACEMENT_3D names to search for
            placement_names = ['MCS', 'CWS', 'PCS']

            found_elements = step_viewer.findPlacementElements(placement_names)

            z = 0
            print("Found elements:")
            print(found_elements)
  
        
            print("Importing file")

            from TopSolid.Kernel.Automating import DocumentId
            from TopSolid.Kernel.Automating import KeyValue
            
            from TopSolid.Kernel.Automating import SmartFrame3D

            outLog = []
            outBadDocumentIds = [DocumentId]

            #result = self.design.Documents.Import(8, inFullName, inOwnerId)

            '''for i in range(0, 100):
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

            file_type = self.design.Application.GetImporterFileType(inImporterIx, uop, out)
            print("file_type :: ", file_type, uop, out)        

            opt = self.design.Application.GetImporterOptions(inImporterIx)
            print("opt :: ", opt, len(opt)) 
            
            # need to change 'SIMPLIFIES_GEOMETRY' to True
            # but is index change from TS version to version, so lets loop through the options and change the one we want
            for i, item in enumerate(opt):
                print(i, item.Key, item.Value)
                if item.Key == "SIMPLIFIES_GEOMETRY":
                    opt[i] = KeyValue("SIMPLIFIES_GEOMETRY", "True")
                    break           

            ''' Default options
            opt[0] = KeyValue("TRANSLATES_ASSEMBLY", "True")
            opt[1] = KeyValue("TRANSLATES_ATTRIBUTES", "True")
            opt[2] = KeyValue("SIMPLIFIES_GEOMETRY", "True")
            opt[3] = KeyValue("SEWS_SHEETS", "False")
            opt[4] = KeyValue("LINEAR_TOLERANCE", "1E-05")
            opt[5] = KeyValue("BODY_DOCUMENT_EXTENSION", ".TopPrt")
            opt[6] = KeyValue("ASSEMBLY_DOCUMENT_EXTENSION", ".TopAsm")
            '''

            for i, item in enumerate(opt):
                print(i, item.Key, item.Value)
                            
            result = self.design.Documents.ImportWithOptions(inImporterIx, opt ,  inFullName,  inOwnerId)

            print(f"Import result: {result}")

            newdoc = result[0]

            #open the file
            print("Opening file", len(newdoc))

            self.open_file(newdoc[0])
            #IGeometries3D.GetFrames 
            frames = self.design.Geometries3D.GetFrames(newdoc[0])
            print("frames :: ", frames, len(frames))
            for frame in frames:
                frame_name = self.get_name(frame)
                print(frame_name)
                #we can create a local def?
                def setFrame (name, frame):
                    frame = SmartFrame3D(frame, False)

                    if name == "MCS":
                        use_frames.MCS = frame
                    elif name == "CWS":
                        use_frames.CWS = frame
                    elif name == "PCS":
                        use_frames.PCS = frame
                    elif name == "WCS":
                        use_frames.WCS = frame
                    elif name == "CSW":
                        use_frames.CSW = frame
                setFrame(frame_name, frame)

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

                inReferenceFrame = frames[0]
                inDirection = SmartDirection3D()
                inDistance = SmartReal()

                Main_SmartFrame = SmartFrame3D( inReferenceFrame, False )
                print("newSmartFrame :: ", Main_SmartFrame)

                for name, placement in found_elements.items():
                    print(f"Found {name} element after import:")
                    print(f"Element Number: {placement.name}")  # Acessa o nome do elemento
                    print(f"Element Content: {placement.coord}, {placement.dir1}, {placement.dir2}\n")  # Acessa as coordenadas e direções

                    '''   if name == "CSW":
                        print(f"{name} :: {info['Element Content']}")
                        z = info['Element Content'][2]'''


                    direction = Direction3D(placement.dir1.x, placement.dir1.y, placement.dir1.z)

                    print("direction :: ", direction)

                    dif = placement.coord.z
                    distance = SmartReal(UnitType.Length, (dif/1000)) #3 = length unit, 0.001 = 1mm
                    

                    print("distance :: ", distance)

                    p3d = Point3D(placement.coord.x, placement.coord.y, placement.coord.z)

                    sdir = SmartDirection3D(direction, p3d)

                    
                    label = ItemLabel(0, 0, name, name)

                    new_frame = SmartFrame3D(Main_SmartFrame, sdir, distance)

                    named_frame = SmartFrame3D(new_frame.ElementId , label, False)


                    print("new_frame :: ", new_frame.Type, named_frame.Type)

                    #start_modif
                    self.start_modif("frame", False)


                    new_frame = self.design.Geometries3D.CreateSmartFrame(newdoc[0],  new_frame) 
                    
                #List<ElementId> GetShapes(DocumentId inDocumentId)
                shapes = self.design.Shapes.GetShapes(newdoc[0])
                print("shapes :: ", shapes, len(shapes))
                for shape in shapes:
                    print(self.get_name(shape), self.get_type(shape))

                axis = self.design.Geometries3D.GetAxes(newdoc[0])
                print("axis :: ", axis)
                for ax in axis:
                    print(self.get_name(ax))

                newAxis = SmartAxis3D(axis[2],  False)
                print("newAxis :: ", newAxis, self.get_name(newAxis))

                #ElementId CreateRevolvedSilhouette(SmartShape inShape,SmartAxis3D inAxis,bool inMerge)

                shape = SmartShape(shapes[0])
                print("shape :: ", shape, self.get_name(shape))

                planes = self.design.Geometries3D.GetPlanes(newdoc[0])
                for plane3d in planes:
                    print(self.get_name(plane3d))

                # SmartPlane3D(planes[0], False)
                #plane = Plane3D(p3d, Direction3D(1, 0, 0), Direction3D(0, 0, 1))
                #splane = SmartPlane3D(plane, 0,0,0,0)

                plane = self.design.Geometries3D.GetAbsoluteXZPlane(newdoc[0])
                splane = SmartPlane3D(plane, False)


                sketch = self.design.Sketches2D.CreateSketchIn3D(newdoc[0], splane,  SmartPoint3D(Point3D(0, 0, 1)), True, SmartDirection3D(Direction3D(1, 0,0), Point3D(1, 0, 0)))



                self.design.Sketches2D.StartModification(sketch)
                revolv = self.design.Sketches2D.CreateRevolvedSilhouette(shape, newAxis, True)
                self.design.Sketches2D.EndModification()


            #SearchProjectByName(string inProjectName)
            func_proj =  self.design.Pdm.SearchProjectByName("TopSolid Machining")
            print("func_proj :: ", func_proj, len(func_proj))

            for func in func_proj:
                print(self.get_name(func), self.get_type(func))
                if self.get_name(func) == "Usinage TopSolid":
                    func_proj = func
                    break
            
            
            #get function PdmDocumentId by Name
            ts_func = self.design.Pdm.SearchDocumentByName(func_proj, "Attachement cylindrique porte outil")              
            print("ts_func :: ", ts_func, len(ts_func), self.get_name(ts_func[0]))
            #Get DocumentId by PdmObjectId
            func_doc = self.design.Documents.GetDocument(ts_func[0])         
            #ElementId ProvideFunction( DocumentId inDocumentId,DocumentId inFunctionId,string inOccurrenceName)                
            prov_func = self.design.Entities.ProvideFunction(newdoc[0], func_doc, "Attachement cylindrique pour l'outil")

            # IGeometries3D - void SetFramePublishingDefinition( inElementId,SmartFrame3D inDefinition)
                    #self.design.Geometries3D.SetFramePublishingDefinition(prov_func, use_frames.CSW)


            
            ts_func = self.design.Pdm.SearchDocumentByName(func_proj, "Profil de révolution pour l'analyse de collision")
            print("ts_func :: ", ts_func, len(ts_func))
            func_doc = self.design.Documents.GetDocument(ts_func[0])
            prov_func = self.design.Entities.ProvideFunction(newdoc[0], func_doc, "Profil def collision")
            
            ts_func = self.design.Pdm.SearchDocumentByName(func_proj, "Système de fixation outil")
            print("ts_func :: ", ts_func, len(ts_func))
            func_doc = self.design.Documents.GetDocument(ts_func[0])
            prov_func = self.design.Entities.ProvideFunction(newdoc[0], func_doc, "Système de fixation vers la machine")
            
            #List<ElementId> GetFunctions( DocumentId inDocumentId )                
            functions = self.design.Entities.GetFunctions(newdoc[0])


            
            print("functions :: ", functions, len(functions))
            for func in functions:
                print(self.get_name(func))
                #GetFunctionDefinition(	ElementId inElementId)
                func_def = self.design.Entities.GetFunctionDefinition(func)
                print("func_def :: ", func_def, self.get_name(func_def))

                #GetFunctionOccurrenceName(	ElementId inElementId ) as String
                func_occ = self.design.Entities.GetFunctionOccurrenceName(func)
                print("func_occ :: ", func_occ)

                #GetFunctionPublishings(ElementId inElementId) as List<ElementId>
                func_pubs = self.design.Entities.GetFunctionPublishings(func)
                print("func_pubs :: ", func_pubs, len(func_pubs))
                self.start_modif(True, False)
                for pub in func_pubs:
                    print(self.get_name(pub))
                    '''
                    ToolingSystemFrame
                    ToolingSystemName
                    ToolingSystemSize
                    '''
                    if self.get_name(pub) == "ToolingSystemFrame":
                        #SetFramePublishingDefinition( inElementId,SmartFrame3D inDefinition)
                        self.design.Geometries3D.SetFramePublishingDefinition(pub, use_frames.PCS)
                        print("pub :: ", pub, self.get_name(pub))
                    elif self.get_name(pub) == "ToolingSystemName":
                        pub_type = self.get_type(pub)
                        print("pub_type :: ", pub_type)
                        if pub_type == "TopSolid.Kernel.DB.D3.Frames.PublishingFrameEntity":
                            self.design.Geometries3D.SetFramePublishingDefinition(pub, use_frames.CSW)
                        else:
                            #IParameters.SetTextPublishingDefinition Method  
                            pub_name = SmartText("HSK")
                            self.design.Parameters.SetTextPublishingDefinition(pub, pub_name)
                        print("pub :: ", pub, self.get_name(pub))
                    elif self.get_name(pub) == "ToolingSystemSize":
                        pub_size = SmartReal(UnitType.Length, (63/1000)) 
                        #IParameters.SetTextPublishingDefinition Method
                        self.design.Parameters.SetRealPublishingDefinition(pub, pub_size)
                        print("pub :: ", pub, self.get_name(pub))
                    elif self.get_name(pub) == "ToolingSystemType":
                        pub_name = SmartText("Mandrin pour queue cylindrique")
                        self.design.Parameters.SetTextPublishingDefinition(pub, pub_name)
                        print("pub :: ", pub, self.get_name(pub))
                    elif self.get_name(pub) == "Revolute Section":
                        #List<ElementId> GetSketches( DocumentId inDocumentId )
                        sketches = self.design.Sketches2D.GetSketches(newdoc[0])
                        print("sketches :: ", self.get_name(sketches[0]), len(sketches))
                        #public SmartSection3D(ElementId inElementId)
                        sect = SmartSection3D(sketches[0])
                        print("sect :: ", sect, self.get_name(sect))
                        #void SetSectionPublishingDefinition(ElementId inElementId,SmartSection3D inDefinition)
                        self.design.Geometries3D.SetSectionPublishingDefinition(pub, sect)


                #print("revolv :: ", revolv)

                out = ""
                print("new_frame :: ", new_frame)


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


    