from math import pi
import winreg
import os
import clr

from databaseTools import update_tool


key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"


#global ts_ext

def get_tool_TSid(tool):
    ts = get_default_lib()

    from TopSolid.Kernel.Automating import DocumentId

    #create new tool id PdmObjectId
    id = DocumentId(tool.TSid)
   
    return id

def initFolders():
    global ts_ext
    global json_data

    try:
        #get topsolid API
        ts = get_default_lib()
        
        #get topsolid types

        current_project = ts_ext.Pdm.GetCurrentProject()
        current_proj_name = getName(current_project)
      
        
        proj_const = ts_ext.Pdm.GetConstituents(current_project)
        print ((str(len(proj_const[0])-1) + " folders in root project, "),end="")# -1 we don't want to count MODELES folder
        print (str(len(proj_const[1])) + " files in root project")
        
        consts = []

        consts = checkFolderOrFile(proj_const)

        print ("consts :: " , consts)
        
        ts_ext.Disconnect()

        return consts        
        
    except Exception as ex:
        # Handle
        print("error :: ", ex)


def GetConstituents(folder):
    global ts_ext

    folder_const = ts_ext.Pdm.GetConstituents(folder)
    folder_name = getName(folder)

    printFolder(folder_const, folder_name)
    #write_json(folder_name, "dir")
    #print ("make path ::" , folder_const,  " :: " , folder_name, " : : ",  export_path_docs)
    
    files = checkFolderOrFile(folder_const)
    print ("GetConstituents :: files :: " , files)
    return files
    

def checkFolderOrFile(folder_const):
    print ("folder path ::")
    
    files = []

    for file in folder_const[1]:
        #printInfo(file, "files")
        filterTypes(file)
        files.append(getName(file))
        
    for dir in folder_const[0]:
        iFiles = GetConstituents(dir)
        for i in iFiles:
            files.append(i)


    return files
       

def filterTypes(file):
    fileType = getType(file)
    #select case fileType     
    match fileType:
        case ".TopPrt":
            print("part file ::", getName(file))
        case ".TopAsm":
            print("assembly file ::", getName(file))
        case ".TopDft":
            #export_pdf(file, export_path)
            print("export pdf ::", getName(file))
            #write_json(getName(file), getType(file))
        case ".TopMillTurn":
            print("cam file ::", getName(file))
        
def getType(obj):
    global ts_ext
    
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



def getName(obj): #get element name - PdmObjectId or DocumentId
    #get python object type
    global ts_ext
    
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
    


def printInfo(file, msg):
    file_name = getName(file)
    file_type = getType(file)
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















def conn(): 

    print ("ts conn")
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


def get_ts_design_dll():
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

    import TopSolid.Kernel.Automating as Automating

    return Automating

def connect():
    top_solid_kernel = get_ts_dll()

    top_solid_kernel_type = top_solid_kernel.TopSolidHostInstance
    ts_ext = clr.System.Activator.CreateInstance(top_solid_kernel_type)
    
    # Connect to TopSolid
    ts_ext.Connect()
    
    return ts_ext
    


def get_ts_ext():
    topsolid_kernel = get_ts_dll()
    if topsolid_kernel is None:
        # Handle error
        return None
    # Get TopSolidHostInstance type
    top_solid_kernel_type = topsolid_kernel.TopSolidHostInstance
    return clr.System.Activator.CreateInstance(top_solid_kernel_type)

def get_default_lib():
    global ts_ext
      # Load TopSolid DLLs
    top_solid_kernel = get_ts_dll()
    if top_solid_kernel is None:
        # Handle error
        return None
    # Get TopSolidHostInstance type
    top_solid_kernel_type = top_solid_kernel.TopSolidHostInstance
    ts_ext = clr.System.Activator.CreateInstance(top_solid_kernel_type)

    # Connect to TopSolid
    ts_ext.Connect()

    print("TopSolid connected successfully!")

    PdmObjectIdType = top_solid_kernel.PdmObjectId

    PdmObjectIdType = ts_ext.Pdm.SearchProjectByName("TopSolid Machining User Tools")
    for i in PdmObjectIdType:
        name = ts_ext.Pdm.GetName(i)
        print("name: ", name)
        if name == "Outils d'usinage utilisateur TopSolid":
            PdmObjectIdType.Clear()
            PdmObjectIdType.Add(i)
            break

    PdmLen =  len(PdmObjectIdType)
    #print("PdmObjectIdType: ", PdmLen)
    return PdmObjectIdType

def EndModif (op, ot):
    global ts_ext
    try:
        ts_ext.Application.EndModification(op, ot)
        print("End modifs")
    except Exception as ex:
        print(str(ex))
        return
    finally:
        print("All modifications ended")
    

def copy_tool(tool, holder):

    global ts_ext
    
    toolModel = ""
    print("tool type: ", tool.toolType)

    #TODO add all tool types to txt external file

    if tool.toolType == 1:#"endMill":
       toolModel = "Side Mill D20 L35 SD20"
    elif tool.toolType == 2:#"radiusMill":
        toolModel = "Radiused Mill D16 L40 r3 SD16"
    elif tool.toolType == 3:#"ballMill":
        toolModel = "Ball Nose Mill D8 L30 SD8"
    elif tool.toolType == 4:#"drill":
        toolModel = "Twisted Drill D10 L35 SD10"
    elif tool.toolType == 5:#"tap":
        toolModel = "Tap M10*1,5 L35 SD10"
    elif tool.toolType == 6:#"tslotMill":
        toolModel = "T Slot Mill D20 L5 SD10"
    elif tool.toolType == 7:#"threadMilll":
        toolModel = "Internal Thread Mill ISO P1,5 L30 SD10"
    else:
        toolModel = "Side Mill D20 L35 SD20"

    """
        Case "endMill", ""
                    model_name = "Side Mill D20 L35 SD20"'"Fraise 2 tailles D20 L35 SD20"
                Case "radiusMill"
                    model_name = "Radiused Mill D16 L40 r3 SD16"'"Fraise torique D16 L40 r3 SD16"
                Case "FRHE"
                    model_name = "Ball Nose Mill D8 L30 SD8"'"Fraise hémisphérique D8 L30 SD8"
                Case "FOP9"
                    model_name = "Spotting Drill D10 SD10"
                Case "FOCA", "FOHS", "drill"
                    model_name = "Twisted Drill D10 L35 SD10"
                Case "ALFI", "reamer"
                    model_name = "Constant Reamer D10 L20 SD9"
                Case Else
                    model
    """

    #print("TS model: ", toolModel)

    # Open project
    modelLib = get_default_lib() #TODO make it connect only one time if we create multiple tools

    #print("TS model lib ID: ", modelLib[0].Id)

    #print("End modif: ")
    EndModif(True, False)

    try:
        # find model tool to copy from default lib
        #output_lib = ts_ext.Pdm.SearchProjectByName("Tool Lib")

        #use current project to create tool
        output_lib = ts_ext.Pdm.GetCurrentProject()

        #print("current lib: ", output_lib)

        toolModelId = ts_ext.Pdm.SearchDocumentByName(modelLib[0], toolModel)
        
        #print("toolModelId: ", len(toolModelId))

        #need a list of PdmObjectId to CopySeveral
        firstTool = toolModelId[0]
        toolModelId.Clear()
        toolModelId.Add(firstTool)

        savedTool = ts_ext.Pdm.CopySeveral(toolModelId, output_lib)

        if savedTool:
            print(f"Tool copied successfully! ", savedTool[0].Id)

        # print("savedTool: ", ts_ext.Documents.Save(tmp))
        #ts_ext.Documents.Open(tmp)

        modif = ts_ext.Application.StartModification("tmp", True)
        print("Start modif: ", modif)
        
        savedToolDocId = ts_ext.Documents.GetDocument(savedTool[0])
        
        #print("Doc Id: ", savedToolDocId.PdmDocumentId)

        savedToolModif = ts_ext.Documents.EnsureIsDirty(savedToolDocId)

        #print("savedToolModif: ", savedToolModif.PdmDocumentId)

        
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

        ts_ext.Parameters.SetTextParameterizedValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Name"), tool.Name)
        #TODO: add tool parameters config
        ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.ManufacturerPartNumber"), str(tool.Name))
        ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Manufacturer"), str(tool.Manuf))
        ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Code"), str(tool.CodeBar))
        ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.PartNumber"), str(tool.Code))
        ts_ext.Parameters.SetBooleanValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.VirtualDocument"), False)

        print("tool: ", tool.Name, tool.Manuf, tool.CodeBar, tool.Code)

        d1 = 0
        d2 = 0
        d3 = 0
        l1 = 0
        l2 = 0
        l3 = 0
        r = 0
        NoTT = 0
        threadPitch = 0.0
        threadTolerance = ""
        print("tool type: ", tool.toolType)


        if tool.threadTolerance and tool.threadTolerance != "0":
            print("thread Tolerance: ", tool.threadTolerance)
            threadTolerance = tool.threadTolerance
            if tool.toolType == 7:
                ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif,"Type"), threadTolerance)
            else:
                ts_ext.Parameters.SetTextValue(ts_ext.Elements.SearchByName(savedToolModif,"Norm"), threadTolerance)
            print("thread Tolerance: ", threadTolerance)

        if tool.threadPitch and int(float(tool.threadPitch != 0)):
            print("thread pitch : ", tool.threadPitch)
            threadPitch = float(tool.threadPitch / 1000).__round__(5)
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"Pitch"), threadPitch)
            print("threadPitch: ", threadPitch)
       
        if tool.NoTT:
            NoTT = tool.NoTT
            ts_ext.Parameters.SetIntegerValue(ts_ext.Elements.SearchByName(savedToolModif, "NoTT"), int(NoTT))
            print("NoTT: ", NoTT)

        if tool.D1:
            if tool.D1 != None and tool.D1 != 0 and tool.D1 != "None": #Fix for D1 = "None"
                d1 = float(tool.D1 / 1000).__round__(5)
                ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"D"), d1)
            
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
                ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"SD"), d3)
                print("d3: ", d3)
        
        if tool.L1:
            l1 = float(tool.L1 / 1000).__round__(5) if tool.L1 is not None and tool.L1 != 0 else 0
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"L"), l1)

        if tool.L2:
            l2 = float(tool.L2 / 1000).__round__(5) if tool.L2 is not None and tool.L2 != 0 else 0

        if tool.L3:
            l3 = float(tool.L3 / 1000).__round__(5) if tool.L3 is not None and tool.L3 != 0 else 0
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"OL"), l3)
        
        if tool.RayonBout:
            if tool.RayonBout != None and tool.RayonBout != 0 and tool.RayonBout != "None":
                r = float(tool.RayonBout / 1000).__round__(5)
                if tool.toolType == 2:
                    ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"r"), r)  
               
        print("d1: " ,d1 , "d2: ", d2, "d3: ", d3, "l1: ", l1, "l2: ", l2, "l3: ", l3, "Z: ", NoTT)
    

        print("tool type parms: ", tool.toolType)

        #if drill
        if tool.toolType == 4:
            if not tool.AngleDeg:
                tool.AngleDeg = 140
            print("AngleDeg: ", tool.AngleDeg)
            tmpAngleRad = int(tool.AngleDeg) * pi / 180
            print("tmpAngleRad: ", tmpAngleRad)
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"A"), tmpAngleRad)
        elif tool.toolType == 5:
            ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"Pitch"), float(tool.threadPitch/1000).__round__(5))
            #ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"L"), l2)
        else:
            if tool.toolType == 7:
                ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"L"), l2)             
            else:
                if l2 > 0:
                    ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"CTS_AD"), d2)
                    ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"CTS_AL"), l2)
      
                  
        from TopSolid.Kernel.Automating import SmartText

        smartTextType = SmartText(ts_ext.Parameters.GetDescriptionParameter(savedToolModif))

        ts_ext.Parameters.PublishText(savedToolModif, "Designation_outil", smartTextType)

        EndModif(True, False)
        
        #ts_ext.Documents.Open(savedToolModif)
        ts_ext.Documents.Save(savedToolModif)

        print("Created tool id: ", savedToolModif.PdmDocumentId)
        tool.TSid = savedToolModif.PdmDocumentId
        #update tool in database
        update_tool(tool)


        if holder:
            copy_holder(savedToolModif)
       
    except Exception as ex:
        EndModif(True,False)

        print("Error copying tool: " + str(ex))

    # Disconnect TopSolid and end the modification
    ts_ext.Disconnect()



def copy_holder(tool):
    global ts_ext

    ts = get_default_lib()
    
    top_solid_kernel_design = get_ts_design_dll()

    ts_design_ext = top_solid_kernel_design.TopSolidDesignHostInstance(ts_ext)

    # Connect to TopSolid
    print(ts_design_ext.Connect())

    EndModif(False, False)


    try:

        # find model holer to copy from default lib
        #output_lib = ts_ext.Pdm.SearchProjectByName("Tool Lib")

        output_lib = ts_ext.Pdm.GetCurrentProject()

        openHolder = ts_ext.Documents.GetOpenDocuments()


        for holder in openHolder:

            print("holder: ", holder.PdmDocumentId, len(openHolder))

            elemModelId = []
            elemModelId.append(holder)

            #toolModelId = ts_ext.Pdm.SearchDocumentByName(modelLib[0], toolModel)
            assemblyModelId = ts_ext.Pdm.SearchDocumentByName(output_lib, "FR + PO")
            print("assemblyModelId: ", assemblyModelId[0].Id)
            
            #elemModelId.append(ts_ext.Pdm.SearchDocumentByName(output_lib, "PO Weldon Ø12 L120"))
            
            elemModelId.append(tool)
            print("elemModelId",elemModelId, len(elemModelId))
            for i in elemModelId:
                print("elemModelId: ", i.PdmDocumentId)


            
            #print("toolModelId len : ", len(toolModelId))
            #for i in toolModelId:
                #print("toolModelId: ", i.Id)


            firstTool = assemblyModelId[0]
            assemblyModelId.Clear()
            assemblyModelId.Add(firstTool)

            #print("toolModelId: ", toolModelId[0].Id, output_lib.Id)


            savedTool = ts_ext.Pdm.CopySeveral(assemblyModelId, output_lib)

            print("savedtool: ",savedTool[0].Id)
            print(f"Tool copied successfully!")

            # print("savedTool: ", ts_ext.Documents.Save(tmp))
            

            

            
            savedToolDocId = ts_ext.Documents.GetDocument(savedTool[0])

            ts_ext.Documents.Open(savedToolDocId)


            ts_ext.Application.StartModification("tmp", True)

            print("savedToolDocId.PdmDocumentId: ", savedToolDocId.PdmDocumentId)
                            
            dirt = ts_ext.Documents.EnsureIsDirty(savedToolDocId)

            print("dirt:: ", dirt.PdmDocumentId)


            ops = ts_ext.Operations.GetOperations(dirt)

            print("ops", ops, len(ops))
            i = 0

            for o in ops:
                if i > 1:
                    break      

                Name = ts_ext.Elements.GetName(o)
                #check if it's an inclusion : 3 first letters of name = "Inc"
                if Name:
                    elemType = getType(o)
                    print("elemType: ", elemType)
                    if elemType == "TopSolid.Cad.Design.DB.Inclusion.InclusionOperation":
                        print("name::: ",Name)
                        print("child: ", o.DocumentId)
                        
                        IsInclusion = ts_design_ext.Assemblies.IsInclusion(o)
                        print("child: ", IsInclusion, o.DocumentId)

                        if IsInclusion == True:
                            ts_ext.Application.StartModification("tmp", True)

                            newTool = elemModelId[i]#ts_ext.Documents.GetDocument(elemModelId[i])
                            i = i + 1
                            print("newTool: ", newTool.PdmDocumentId)

                            ts_design_ext.Assemblies.RedirectInclusion(o, newTool)
                            
                            EndModif(True,True)
            
            ts_ext.Application.StartModification("tmp", True)

            name = "[Designation_outil] + [Designation_po]"
            ts_ext.Parameters.SetTextParameterizedValue(ts_ext.Elements.SearchByName(dirt, "$TopSolid.Kernel.TX.Properties.Name"), name)

            EndModif(True, False)
            
            ts_ext.Documents.Save(savedToolDocId)

    except Exception as ex:
        print("Error copying tool: " + str(ex))
        EndModif(False, False)

