import winreg
import os
import clr

key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

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
        top_solid_kernel_path = os.path.join(
        top_solid_path, "bin", "TopSolid.Kernel.Automating.dll")
        print(f"Loading dll: {top_solid_kernel_path}")
        clr.AddReference(top_solid_kernel_path)
        
        import TopSolid.Kernel.Automating as Automating
        
        top_solid_kernel = Automating

        top_solid_kernel_type = top_solid_kernel.TopSolidHostInstance
        ts_ext = clr.System.Activator.CreateInstance(top_solid_kernel_type)

        # Connect to TopSolid
        ts_ext.Connect()

        #print connected with version
        print("TopSolid " + top_solid_version + " connected successfully!")

    except Exception as ex:
        # Handle
        print("not found")



def get_version():
    try:
        sub_keys = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        sub_keys_count = winreg.QueryInfoKey(sub_keys)[0]
        last_sub_key = winreg.EnumKey(sub_keys, sub_keys_count - 1)
        return last_sub_key
    except Exception as ex:
        # Handle
        return "not found"


def get_top_solid_path():
    top_solid_version = get_version()

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path +
                             "\\" + top_solid_version, 0, winreg.KEY_READ)
        value = winreg.QueryValueEx(key, "InstallDir")
        return value[0]
    except Exception as ex:
        # Handle exception
        return ex


def get_ts_dll():
    top_solid_path = get_top_solid_path()
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

    return PdmObjectIdType

def EndModif ():
    global ts_ext
    try:
        ts_ext.Application.EndModification(False, False)
        print("End modifs")
    except Exception as ex:
        print(str(ex))
        return
    finally:
        print("All modifications ended")
    

def copy_tool(tool):

    global ts_ext
    
    toolModel = ""

    #tool switch case
    if tool.Type == "endMill":
       toolModel = "Side Mill D20 L35 SD20"
    elif tool.Type == "radiusMill":
        toolModel = "Radiused Mill D16 L40 r3 SD16"
    elif tool.Type == "ballMill":
        toolModel = "Ball Nose Mill D8 L30 SD8"
    else:
        toolModel = "Side Mill D20 L35 SD20"

    print("toolModel: ", toolModel)

    # Open project
    modelLib = get_default_lib()

    print("model lib: ", modelLib[0].Id)

    print("End modif: ")
    EndModif()

    try:
        # find model tool to copy from default lib
        output_lib = ts_ext.Pdm.SearchProjectByName("Tool Lib")

        toolModelId = ts_ext.Pdm.SearchDocumentByName(modelLib[0], toolModel)

        firstTool = toolModelId[0]
        toolModelId.Clear()
        toolModelId.Add(firstTool)

        print("toolModelId: ", toolModelId[0].Id)


        savedTool = ts_ext.Pdm.CopySeveral(toolModelId, output_lib[0])

        print("savedtool: ",savedTool[0].Id)
        print(f"Tool copied successfully!")

        # print("savedTool: ", ts_ext.Documents.Save(tmp))
        #ts_ext.Documents.Open(tmp)

        modif = ts_ext.Application.StartModification("tmp", True)
        print("Start modif: ", modif)
        
        savedToolDocId = ts_ext.Documents.GetDocument(savedTool[0])
        
        print("Doc Id: ", savedToolDocId.PdmDocumentId)

        savedToolModif = ts_ext.Documents.EnsureIsDirty(savedToolDocId)

        print("savedToolModif: ", savedToolModif.PdmDocumentId)
        

        ts_ext.Parameters.SetTextParameterizedValue(ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Name"), tool.ManufRef)
        
        Nott = ts_ext.Parameters.SetIntegerValue(ts_ext.Elements.SearchByName(savedToolModif, "NoTT"), int(tool.NoTT))
   
        d1 = tool.D1 / 1000 if tool.D1 is not None and tool.D1 != 0 else 0
        d2 = tool.D2 / 1000 if tool.D2 is not None and tool.D2 != 0 else  d1-(0.2/1000)
        d3 = tool.D3 / 1000 if tool.D3 is not None and tool.D3 != 0 else 0
        l1 = tool.L1 / 1000 if tool.L1 is not None and tool.L1 != 0 else 0
        l2 = tool.L2 / 1000 if tool.L2 is not None and tool.L2 != 0 else 0
        l3 = tool.L3 / 1000 if tool.L3 is not None and tool.L3 != 0 else 0

        r = tool.RayonBout / 1000

        print("d1: " ,d1 , "d2: ", d2, "d3: ", d3, "l1: ", l1, "l2: ", l2, "l3: ", l3)
    
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"D"), d1)
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"CTS_ED"), d2)
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"SD"), d3)
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"L"), l1)
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"CTS_EL"), l2)
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"OL"), l3)
        ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"r"), r)

        ts_ext.Application.EndModification(True, False)

        ts_ext.Documents.Open(savedToolModif)
        ts_ext.Documents.Save(savedToolModif)
       
    except Exception as ex:
        EndModif()

        print("Error copying tool: " + str(ex))

    # Disconnect TopSolid and end the modification
    ts_ext.Disconnect()
