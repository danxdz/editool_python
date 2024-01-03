from math import pi
import winreg
import os
import clr
import wx


from tool import ToolsDefaultsData
from tool import ToolsCustomData


key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"


def setRealParameter(ts_ext, doc, paramName, value):
    #setRealParameter(savedToolModif,"A_T", chamfer)

    from TopSolid.Kernel.Automating import SmartReal
    from TopSolid.Kernel.Automating import UnitType

    SmartRealNewParam = SmartReal(UnitType(2),value) # 2 :: UnitType - Angle - 2 - Plane angle.                            

    getOps = ts_ext.Operations.GetOperations (doc)
    for op in getOps:
        children = ts_ext.Operations.GetChildren(op)
        for child in children:
            childName = ts_ext.Elements.GetName(child)
            if childName == paramName:
                print("childName: ", childName, child.GetType())                
                #smartRealParam = ts_ext.Parameters.GetSmartRealParameterCreation(op) 
                setParam = ts_ext.Parameters.SetSmartRealParameterCreation(op, SmartRealNewParam)
                print(f"set {paramName} : {SmartRealNewParam} : {value} : {setParam}")




#*************** TS functions *****************

def get_tool_TSid(tool):

    tsConn()

    from TopSolid.Kernel.Automating import DocumentId
    #create new tool id PdmObjectId
    id = DocumentId(tool.TSid)   
    return id


def tsConn(): 

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
        # *************************
        top_solid_kernel_path = os.path.join(top_solid_path, "bin", "TopSolid.Kernel.Automating.dll")
        print(f"Loading dll: {top_solid_kernel_path}")
        clr.AddReference(top_solid_kernel_path)
        
        import TopSolid.Kernel.Automating as Automating
        from TopSolid.Kernel.Automating import PdmObjectId
        from TopSolid.Kernel.Automating import DocumentId
        
        top_solid_kernel = Automating

        top_solid_kernel_type = top_solid_kernel.TopSolidHostInstance
        ts_ext = clr.System.Activator.CreateInstance(top_solid_kernel_type)

        clr.setPreload(True)


        # Connect to TopSolid
        ts_ext.Connect()

        #print connected with version
        print("TopSolid " + top_solid_version + " connected successfully!")

        return ts_ext


    except Exception as ex:
        # Handle
        print("not found")



def get_version():
    try:
        sub_keys = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        sub_keys_count = winreg.QueryInfoKey(sub_keys)[0]
        last_sub_key = winreg.EnumKey(sub_keys, sub_keys_count - 1)
        return last_sub_key
    except Exception as ex:
        # Handle
        return "not found"


def get_top_solid_path():
    top_solid_version = get_version()

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path + "\\" + top_solid_version, 0, winreg.KEY_READ)
        value = winreg.QueryValueEx(key, "InstallDir")
        return (value[0], top_solid_version)
    except Exception as ex:
        # Handle exception
        return ex






def get_ts_design_ext():
    ts = get_top_solid_path()
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

def get_ts_dll():
    ts = get_top_solid_path()
    top_solid_path = ts[0]
    if top_solid_path is None:
        # Handle
        return None

    # Load DLLs
    top_solid_kernel_sx_path = os.path.join(
        top_solid_path, "bin", "TopSolid.Kernel.SX.dll")
    print(f"Loading dll: {top_solid_kernel_sx_path}")
    clr.AddReference(top_solid_kernel_sx_path)
    # *************************

    top_solid_kernel_path = os.path.join(
        top_solid_path, "bin", "TopSolid.Kernel.Automating.dll")
    print(f"Loading dll: {top_solid_kernel_path}")
    clr.AddReference(top_solid_kernel_path)

    clr.setPreload(True)


    import TopSolid.Kernel.Automating as Automating

    return Automating


def get_default_lib(ts_ext):
      # Load TopSolid DLLs
    if ts_ext is None:
        # Handle error
        return None
    
    from TopSolid.Kernel.Automating import PdmObjectId
    
    PdmObjectIdType = PdmObjectId

    PdmObjectIdType = ts_ext.Pdm.SearchProjectByName("TopSolid Machining User Tools")
    for i in PdmObjectIdType:
        name = ts_ext.Pdm.GetName(i)
        #print("name: ", name)
        if name == "Outils d'usinage utilisateur TopSolid":
            PdmObjectIdType.Clear()
            PdmObjectIdType.Add(i)
            break

    #PdmLen =  len(PdmObjectIdType)
    #print("PdmObjectIdType: ", PdmLen)
    return PdmObjectIdType

def EndModif (ts_ext, op, ot):
    try:
        ts_ext.Application.EndModification(op, ot)
        print("End modifs")
    except Exception as ex:
        print(str(ex))
        return
    finally:
        print("All modifications ended")
    



#***************************************************************************




def copy_tool(tool, holder): #holder = true or false

    #load default data
    toolDefaultData = ToolsDefaultsData()

    toolData = ToolsCustomData()
    toolData = toolData.getCustomTsModels()
    
    ts_ext = tsConn()
 
    #uncomment to prevent get TS blocked, may output an error "No modification to end."
    #EndModif(ts_ext, True, False)

    try:
        
        #search for editool project for custom tools models and tool assembly templates
        output_lib = ts_ext.Pdm.SearchProjectByName("editool")
        output_lib = output_lib[0]
        if output_lib:
            
            # open it to create tool
            ts_ext.Pdm.OpenProject(output_lib)
                            
            # get custom tool model name
            customToolModel = toolData.tsModels[tool.toolType]
            # if custom model exist
            if customToolModel:
                print("custom model: ", customToolModel)
                modelLib = output_lib
                toolToCopy_ModelId = ts_ext.Pdm.SearchDocumentByName(modelLib, customToolModel)
            else:
                # or get ts default model 
                modelLib = get_default_lib(ts_ext) # TODO make it connect only one time if we create multiple tools
                modelLib = modelLib[0]
                tsDefaultModel = toolDefaultData.tsModels[tool.toolType]
                toolToCopy_ModelId = ts_ext.Pdm.SearchDocumentByName(modelLib, tsDefaultModel)
        else:
            # if not editool project :: use current project to create tools
            output_lib = ts_ext.Pdm.GetCurrentProject()
            print("GetCurrentProject :: ", output_lib.Id)

        print(f"*** copy tool ***  {toolDefaultData.toolTypes[tool.toolType]} :: from: {ts_ext.Pdm.GetName(modelLib)} :: model : {ts_ext.Pdm.GetName(toolToCopy_ModelId[0])} :: to : {ts_ext.Pdm.GetName(output_lib)}")
        
        
        #for i in toolModelId:
        #    print("toolModelId: ", i.Id)

        # need a list of PdmObjectId to CopySeveral, with only one tool model
        firstTool = toolToCopy_ModelId[0]
        toolToCopy_ModelId.Clear()
        toolToCopy_ModelId.Add(firstTool)


        #print("GetCurrentProject :: ", output_lib.Id)

        # find model tool to copy from default lib
        #print("toolModelId: ", len(toolModelId))


        savedTool = ts_ext.Pdm.CopySeveral(toolToCopy_ModelId, output_lib)

        if savedTool:
            #print(f"Tool copied successfully!  {ts_ext.Pdm.GetName(savedTool[0])} ::  {savedTool[0].Id}")
            print(f"tool model copied successfully!  {ts_ext.Pdm.GetName(savedTool[0])} ::  {savedTool[0].Id}")

        savedToolDocId = ts_ext.Documents.GetDocument(savedTool[0])

        modif = ts_ext.Application.StartModification("saveTool", True)
        #print("Start modif: ", modif, savedToolDocId.PdmDocumentId)

        savedToolModif = ts_ext.Documents.EnsureIsDirty(savedToolDocId)

        #print("dirt savedToolModif: ", savedToolModif.PdmDocumentId)

        
        #Debug -> get elements param list
        """
        sys_pard = ts_ext.Elements.GetElements(savedToolModif)
        print("sys_pard: ", sys_pard)
        for i in range(len(sys_pard)):
            print("sys_pard: ", sys_pard[i])
            print("sys_pard: ", ts_ext.Elements.GetName(sys_pard[i]))            
            if ts_ext.Elements.GetName(sys_pard[i]) == "":
                print("sys_pard: ", ts_ext.Elements.GetDescription(sys_pard[i]))
        
        exit()
        """

        ts_ext.Parameters.SetTextParameterizedValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Name"), tool.name)
        #TODO: add tool parameters config
        ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.ManufacturerPartNumber"), str(tool.name))
        ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Manufacturer"), str(tool.mfr))
        ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Code"), str(tool.codeBar))
        ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.PartNumber"), str(tool.code))
        ts_ext.Parameters.SetBooleanValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.VirtualDocument"), False)

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
        print("tool type: ", tool.toolType)


        if tool.toolType == 8:#tap

            if tool.threadTolerance and tool.threadTolerance != "None" and tool.threadTolerance != "":
                ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif,"Type"), threadTolerance)
            else:
                ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif,"Norm"), threadTolerance)

        if tool.threadPitch and int(float(tool.threadPitch != 0)):
            print("thread pitch : ", tool.threadPitch)
            threadPitch = float(tool.threadPitch / 1000).__round__(5)
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"Pitch"), threadPitch)

        if tool.z:
            z = tool.z
            ts_ext.Parameters.SetIntegerValue(ts_ext.Elements.SearchByName(savedToolModif, "NoTT"), int(z))
            print("z: ", z)

        if tool.D1:
            if tool.D1 != None and tool.D1 != 0 and tool.D1 != "None": #Fix for D1 = "None"
                d1 = float(tool.D1 / 1000).__round__(5)
            
        if tool.D2: #Fix for D2 = "None"
            if tool.D2 != None and tool.D2 != 0 and tool.D2 != "None":
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
            print("cornerRadius: ", tool.cornerRadius, tool.toolType  )
            if tool.cornerRadius != None and tool.cornerRadius != 0 and tool.cornerRadius != "None":
                r = float(tool.cornerRadius / 1000).__round__(5)
                if tool.toolType == 1:#radius mill
                    ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"r"), r)  
               
        
        print(f" {tool.toolType} :: {d1} :  {d2} : {d3} : {l1} : {l2} : {l3} : {z}")



        #set tool parameters


        if tool.toolType == 6:#center drill
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"D1"), d3)    
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"D2"), d1)    
            
            #need to convert angle from deg to rad
            print("AngleDeg: ", tool.neckAngle, "chamfer: ", tool.chamfer)
            angle = float(tool.neckAngle) * 1
            chamfer = float(tool.chamfer) * 1

            chamfer = float(chamfer * pi / 180).__round__(5)
            angle = float(angle * pi / 180).__round__(5)

            setRealParameter(ts_ext, savedToolModif,"A_T", chamfer)
                                                                
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"A"), angle)      
       
        else:
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"D"), d1)                



        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"SD"), d3)                
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"L"), l1)                
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"OL"), l3)



        #if drill
        if tool.toolType == 7:#drill
            if not tool.neckAngle:
                tool.neckAngle = 140
            print("AngleDeg: ", tool.neckAngle)
            tmpAngleRad = int(tool.neckAngle) * pi / 180
            print("tmpAngleRad: ", tmpAngleRad)
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"A"), tmpAngleRad)
        
        #thread mill
        elif tool.toolType == 9:
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"Pitch"), float(tool.threadPitch/1000).__round__(5))
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"LH"), l2)

           

            getSketchs = ts_ext.Sketches2D.GetSketches(savedToolModif)
            print("getSketch: ", getSketchs, len(getSketchs))
            for sketch in getSketchs:
                sketchName = ts_ext.Elements.GetName(sketch)
                if sketchName == "ShankSketch":
                        print("childName: ", sketchName, sketch.GetType())
                        consts = ts_ext.Elements.GetConstituents(sketch)
                        print("consts: ", consts,len(consts))
                        props = ts_ext.Elements.GetProperties(sketch)   
                        print("props: ", props,len(props))
          
                        for p in props:
                            print("prop: ",p)

                        for i in consts:
                            constName = ts_ext.Elements.GetName(i)
                            if constName == "Dimension 3" or constName == "Dimension 4":
                                print("consts: ", constName, i.GetType())
                                value = ts_ext.Elements.GetTypeFullName(i)
                                modif = ts_ext.Elements.IsModifiable(i)
                                delet = ts_ext.Elements.IsDeletable(i)


                                print("value: ", value, modif, delet )
                               
                                #propType = ts_ext.Elements.Delete(i)
                                #print("propType: ", propType)
                                
                                    


                              

                        

                                    






        
        #if spot drill
        elif tool.toolType == 5:#spot drill
                ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"L"), l2)
        
        else:
                
            if l2 > 0:
                ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"CTS_AD"), d2)
                ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"CTS_AL"), l2)
      
                  
        from TopSolid.Kernel.Automating import SmartText

        smartTextType = SmartText(ts_ext.Parameters.GetDescriptionParameter(savedToolModif))
        print("smartTextType: ", smartTextType)

        ts_ext.Parameters.PublishText(savedToolModif, "FR", smartTextType)

        EndModif(ts_ext, True, False)
        
        ts_ext.Documents.Save(savedToolModif)
        ts_ext.Documents.Open(savedToolModif)


        print("Created tool with id: ", savedToolModif.PdmDocumentId)
        tool.TSid = savedToolModif.PdmDocumentId
        
        #update tool in database

        ###############update_tool(tool)

        if holder:
            copy_holder(ts_ext, savedToolModif)
       
    except Exception as ex:
        EndModif(ts_ext, True,False)

        print("Error copying tool: " + str(ex))

    # Disconnect TopSolid and end the modification
    ts_ext.Disconnect()



def copy_holder(ts_ext, tool):

    if ts_ext is None:
        print("ts_ext is not connected")
        ts_ext = tsConn()
    
    top_solid_kernel_design = get_ts_design_ext()

    ts_design_ext = top_solid_kernel_design.TopSolidDesignHostInstance(ts_ext)

    # Connect to TopSolid
    print(ts_design_ext.Connect())

    EndModif(ts_ext, False, False)


    try:

        # use current project to create assembled tool
        output_lib = ts_ext.Pdm.GetCurrentProject()
        #print("GetCurrentProject :: ", output_lib.Id)
        openDocs = ts_ext.Documents.GetOpenDocuments()
        print("openDocs: ", len(openDocs))

        holdersFound = False

        #check if any holder is open in TS
        for holder in openDocs:
            print("holder: ", holder.PdmDocumentId)
            #check if it not an assembly, because holder is one part
            if ts_design_ext.Assemblies.IsAssembly(holder) == False:
                if ts_design_ext.Parts.IsPart(holder) == True:
                    #get functions of the part
                    holderFunctions = ts_ext.Entities.GetFunctions(holder)
                    if holderFunctions:
                        print("toolModelen: ", len(holderFunctions))
                        if holderFunctions and len(holderFunctions) > 0:
                            for  i in holderFunctions:
                                print("holderFunctions", ts_ext.Elements.GetName(i))
                                function = ts_ext.Elements.GetFriendlyName(i)
                                print("function: ", function)
                                if function == "Système de fixation porte-outil <ToolingHolder_1>" or function == "Attachement cylindrique porte outil <CylindricalToolingHolder_1>" or function == "Attachement cylindrique porte outil <ToolingHolder_1>": #TODO: check if exist a better way to identify holder
                                    print(f"found : {function}")
                                    holdersFound = True
                                    break
                    
                    if holdersFound == True:
                        print("holderFound: ", holdersFound)
                        
                        elemModelId = []
                        elemModelId.append(holder)

                        #get the assembly model 
                        assemblyModelId = ts_ext.Pdm.SearchDocumentByName(output_lib, "FR + PO")
                        print("assemblyModelId: ", assemblyModelId[0].Id)
                                            
                        elemModelId.append(tool)

                        #print("elemModelId",elemModelId, len(elemModelId))
                        #for i in elemModelId:
                        #    print("elemModelId: ", i.PdmDocumentId)

                        # need a list of PdmObjectId to CopySeveral, but we need to copy only the first tool
                        firstTool = assemblyModelId[0]
                        assemblyModelId.Clear()
                        assemblyModelId.Add(firstTool)

                        newTool = ts_ext.Pdm.CopySeveral(assemblyModelId, output_lib)

                        print(f"Tool copied successfully!", newTool[0].Id)
                        
                        newToolDocId = ts_ext.Documents.GetDocument(newTool[0])

                        ts_ext.Documents.Open(newToolDocId)

                        ts_ext.Application.StartModification("tmp", True)
                                        
                        dirt = ts_ext.Documents.EnsureIsDirty(newToolDocId)

                        print(f"dirt:: {dirt.PdmDocumentId} :: {newToolDocId.PdmDocumentId}")

                        ops = ts_ext.Operations.GetOperations(dirt)

                        print("ops", ops, len(ops))
                        i = 0

                        for o in ops:
                            if i > 1:
                                break      

                            Name = ts_ext.Elements.GetName(o)
                            #check if it's an inclusion : 3 first letters of name = "Inc"
                            if Name:
                                elemType = getType(ts_ext, o)
                                print("elemType: ", elemType)
                                if elemType == "TopSolid.Cad.Design.DB.Inclusion.InclusionOperation":
                                    print("name::: ",Name)
                                    print("child: ", o.DocumentId)
                                    
                                    IsInclusion = ts_design_ext.Assemblies.IsInclusion(o)
                                    print("child: ", IsInclusion, o.DocumentId)

                                    if IsInclusion == True:
                                        ts_ext.Application.StartModification("tmp", True)

                                        newTool = elemModelId[i]  #ts_ext.Documents.GetDocument(elemModelId[i])
                                        i = i + 1
                                        print("newTool: ", newTool.PdmDocumentId)

                                        ts_design_ext.Assemblies.RedirectInclusion(o, newTool)
                                        
                                        EndModif(ts_ext, True,True)
                        
                        ts_ext.Application.StartModification("tmp", True)

                        name = "[FR] + [PO]"

                        ts_ext.Parameters.SetTextParameterizedValue(ts_ext.Elements.SearchByName(dirt, "$TopSolid.Kernel.TX.Properties.Name"), name)

                        EndModif(ts_ext, True, False)
                        ts_ext.Documents.Save(newToolDocId)

                        
                    
                    
        if holdersFound == False:
            print("holder not found")
            noTool = wx.MessageBox('holder not open on TS, try to open and retry', 'Warning', wx.OK | wx.ICON_QUESTION)
    
                
                    

    except Exception as ex:
        print("Error copying tool: " + str(ex))
        EndModif(ts_ext, False, False)




#*************** folders and files functions *****************

def initFolders():
    global json_data

    try:
        #get topsolid API
        ts_ext = tsConn()
        
        #get topsolid types

        current_project = ts_ext.Pdm.GetCurrentProject()
        current_proj_name = getName(ts_ext, current_project)
      
        
        proj_const = ts_ext.Pdm.GetConstituents(current_project)
        print ((str(len(proj_const[0])-1) + " folders in root project, "),end="")# -1 we don't want to count MODELES folder
        print (str(len(proj_const[1])) + " files in root project")
        
        consts = []

        consts = checkFolderOrFile(ts_ext, proj_const)

        print ("consts :: " , consts)
        
        ts_ext.Disconnect()

        return consts        
        
    except Exception as ex:
        # Handle
        print("error :: ", ex)


def GetConstituents(ts_ext, folder):


    folder_const = ts_ext.Pdm.GetConstituents(folder)
    folder_name = getName(ts_ext, folder)

    printFolder(folder_const, folder_name)
    #write_json(folder_name, "dir")
    #print ("make path ::" , folder_const,  " :: " , folder_name, " : : ",  export_path_docs)
    
    files = checkFolderOrFile(ts_ext, folder_const)
    #print ("GetConstituents :: files :: " , files)
    return files
    

def checkFolderOrFile(ts_ext, folder_const):
    print ("folder path ::")
    
    files = []

    for file in folder_const[1]:
        #printInfo(file, "files")
        filterTypes(ts_ext, file)
        files.append(getName(ts_ext, file))
        
    for dir in folder_const[0]:
        iFiles = GetConstituents(ts_ext, dir)
        for i in iFiles:
            files.append(i)

    return files

def filterTypes(ts_ext, file):
    fileType = getType(ts_ext, file)
    #select case fileType     
    match fileType:
        case ".TopPrt":
            print("part file ::", getName(ts_ext, file))
        case ".TopAsm":
            print("assembly file ::", getName(ts_ext, file))
        case ".TopDft":
            #export_pdf(file, export_path)
            print("export pdf ::", getName(ts_ext, file))
            #write_json(getName(file), getType(file))
        case ".TopMillTurn":
            print("cam file ::", getName(ts_ext, file))
        
def getType(ts_ext, obj):

    from TopSolid.Kernel.Automating import PdmObjectId
    from TopSolid.Kernel.Automating import DocumentId
    from TopSolid.Kernel.Automating import ElementId
    
    ts_type = ""

    #get python object type
    obj_type = type(obj)
    #print ("getType :: obj_type ::" , obj_type)
    if obj_type is PdmObjectId:
        raw_ts_type = ts_ext.Pdm.GetType(obj)
        #print ("getType :: raw ts_type ::" , raw_ts_type[0])
        if str(raw_ts_type[0]) == "Folder":
            ts_type = str(raw_ts_type[0])
        else:
            ts_type = str(ts_ext.Pdm.GetType(obj)[1])
    elif obj_type is DocumentId:
        isPart = ts_ext.Documents.IsPart(obj)
        print ("getType :: isPart ::" , isPart)
        ts_type = str(ts_ext.Documents.GetType(obj)[0])
    #print ("getType :: res obj_type :: ::" , ts_type)
    elif obj_type is ElementId:
        ts_type = str(ts_ext.Elements.GetTypeFullName(obj))
        #print ("getType :: res elem_type :: ::" , ts_type)
    return ts_type



def getName(ts_ext, obj): #get element name - PdmObjectId or DocumentId
    #get python object type
    
    from TopSolid.Kernel.Automating import PdmObjectId
    from TopSolid.Kernel.Automating import DocumentId
    from TopSolid.Kernel.Automating import ElementId

    obj_type = type(obj)
    #print ("name obj_type ::" , obj_type)
    if obj_type is PdmObjectId:
        name = str(ts_ext.Pdm.GetName(obj))
    elif obj_type is DocumentId:
        name = str(ts_ext.Documents.GetName(obj))
    #print ("get name ::" , name)
    return name
    

def printInfo(ts_ext, file, msg):
    file_name = getName(ts_ext, file)
    file_type = getType(ts_ext, file)
    print (msg , " ; ", file_name , " ; " ,file_type )
    #write_json(file_name, file_type)


def printFolder (folder_const, folder_name):
    if len(folder_const[0])>0 or len(folder_const[1])>0:
        print (str("dir " + folder_name + " @ " + " have "), end="")
        if len(folder_const[0])>0:
            print (str(len(folder_const[0])) + " folders ",end="")
        if len(folder_const[1])>0:
            print (str(len(folder_const[1])) + " files")
        else:
            print ("")
    else:
        print ("dir " + folder_name + " is empty")


def make_path(path):
    try:
        res = os.makedirs(path)
        print ("MAKE_PATH :: dir created :: ",path, res)
    except Exception as ex:
        # Handle
        print("error :: ", ex)
        pass

def write_json(key, value):
    #need to add data at end of json file
    json_data[key] = value
    #print ("WRITE_JSON :: write  ::" , key , "::" , value)