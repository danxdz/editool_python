import winreg
import os
import clr

key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

custom_tools_project_name = "Tool Lib"

ts_ext = None

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

def get_ts_design_dll():
    top_solid_path = get_top_solid_path()
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
    top_solid_path = get_top_solid_path()
    if top_solid_path is None:
        # Handle
        return None

    # Load DLLs
    top_solid_kernel_sx_path = os.path.join(
        top_solid_path, "bin", "TopSolid.Kernel.SX.dll")
    print(f"Loading dll: {top_solid_kernel_sx_path}")
    clr.AddReference(top_solid_kernel_sx_path)
    # *************************1
    top_solid_kernel_path = os.path.join(
        top_solid_path, "bin", "TopSolid.Kernel.Automating.dll")
    print(f"Loading dll: {top_solid_kernel_path}")
    clr.AddReference(top_solid_kernel_path)
    
    #set preload to true to load all dependent dlls
    clr.setPreload(True)

    import TopSolid.Kernel.Automating as Automating

    """
    for i in Automating.__dict__:
        print("i: ", i)

    ert = Automating.UserQuestion("zerzer", "zerzer")
    print("ert: ", ert)
    """

    return Automating


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
            print("found")
            PdmObjectIdType.Clear()
            PdmObjectIdType.Add(i)
            break
    print("PdmObjectIdType: ", len(PdmObjectIdType))

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
    

def copy_tool(toolModel):

    global ts_ext
    # Open project
    modelLib = get_default_lib()

    print("model lib: ", modelLib[0].Id)
    #EndModif(False, False)

    try:
        #ts_ext.Application.EndModification(False, True)

        # find model tool to copy from default lib
        #output_lib = ts_ext.Pdm.SearchProjectByName("Tool Lib")
        output_lib = ts_ext.Pdm.GetCurrentProject()

        toolModelId = ts_ext.Pdm.SearchDocumentByName(modelLib[0], toolModel)
        elemModelId = ts_ext.Pdm.SearchDocumentByName(modelLib[0], "Side Mill D20 L35 SD20")

        newModel = ts_ext.Pdm.SearchDocumentByName(output_lib, "Foret")
        print("newModel: ", newModel, len(newModel))
        for i in newModel:
            print("i: ", i.Id)


        print("elemModelId: ", elemModelId[0])

        print("toolModelId len : ", len(toolModelId))
        for i in toolModelId:
            print("toolModelId: ", i.Id)

        #firstTool = toolModelId[0]
        firstTool = newModel[0]
        toolModelId.Clear()
        toolModelId.Add(firstTool)

        print("toolModelId: ", toolModelId[0].Id)


        savedTool = ts_ext.Pdm.CopySeveral(toolModelId, output_lib)

        print("savedtool: ",savedTool[0].Id)
        print(f"Tool copied successfully!")

        # print("savedTool: ", ts_ext.Documents.Save(tmp))
        #ts_ext.Documents.Open(tmp)

        
        savedToolDocId = ts_ext.Documents.GetDocument(savedTool[0])
        print("savedToolDocId.PdmDocumentId: ", savedToolDocId.PdmDocumentId)

        top_solid_kernel_design = get_ts_design_dll()
 
        ts_design_ext = top_solid_kernel_design.TopSolidDesignHostInstance(ts_ext)

        # Connect to TopSolid
        print(ts_design_ext.Connect())

        dd = get_ts_dll()
        question = dd.UserQuestion("Do you want to open the tool?", "zerzer")


        isAssembly = ts_design_ext.Assemblies.IsAssembly(savedToolDocId)
        print("assembly: ", isAssembly)


        
        parts = ts_design_ext.Assemblies.GetParts(savedToolDocId)
        print("parts: ", parts)
        #define type as outPart as TopSolid.Kernel.Automating.ElementId
        outPart = clr.System.Activator.CreateInstance(dd.ElementId)

        for part in parts:
            print("part: ", part)
            ask = ts_design_ext.Assemblies.AskOccurrence(question,True,True,True,True,True,part,outPart)
            print("ask: ", ask[1].DocumentId.PdmDocumentId)
            child = ts_design_ext.Assemblies.IsInclusion(part)
            print("child: ", child)
            local = ts_design_ext.Assemblies.IsLocalPartOrLocalAssembly(part)
            print("local: ", local)
            occ = ts_design_ext.Assemblies.GetOccurrenceDefinition(part)
            print("occ: ", occ.PdmDocumentId)
            pp = ts_design_ext.Parts.IsPart(occ)
            print("pp: ", pp)
            const = ts_ext.Elements.GetName(part)
            print("const: ", const)

            #ts_ext.Application.StartModification("tmp", True)
            #ts_ext.Documents.EnsureIsDirty(savedToolDocId)
            #newTool = ts_ext.Documents.GetDocument(elemModelId[0])
            #print("newTool: ", newTool.PdmDocumentId)
            #ts_design_ext.Assemblies.RedirectInclusion(part, newTool)

            """            
            docId = ts_ext.Elements.GetProperties(part)
            print("docId: ", docId)
            for i in docId:
                print("i: ", i)
                if i == "$TopSolid.Kernel.TX.Properties.Name":
                    name = ts_ext.Elements.GetPropertyTextValue(part, i)
                    print("name: ", name)
            """
            
        exit()
    except Exception as ex:
        print("Error copying tool: " + str(ex))
        EndModif(False,False)

    # Disconnect TopSolid and end the modification
    #top_solid_ext.Disconnect()


def get_user_input():
    # Mostrar lista de opções disponíveis
    print("Tipos de ferramenta disponíveis:")
    print("1. Fraises 2 tailles")
    print("2. Fraises toriques")
    print("3. Fraises hémisphérique")
    print("4. Forets à pointer")
    print("5. Forets hélicoidaux")
    print("6. Alésoirs fixes")
    
    # Solicitar ao usuário o tipo de ferramenta
    while True:
        try:
            opcao = int(input("Digite o número correspondente ao tipo de ferramenta desejado: "))
            if opcao in [1, 2, 3, 4, 5, 6]:  # Verificar se a opção é válida
                return opcao
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Opção inválida. Tente novamente.")






def modifyToolParams(saved_tool):
    global ts_ext

    try:
        if saved_tool is None:
            print(f"Can't copy file")
            ts_ext.Application.EndModification(True, False)
            return
       
        if not ts_ext.Application.StartModification("model_fr", True) :
            print("StartModification failure")
            ts_ext.Application.EndModification(True, False)
            return
            
        ts_ext.Application.StartModification("model_fr", True)

        tmp =  ts_ext.Documents.GetDocument(saved_tool[0])
        
        ts_ext.Documents.EnsureIsDirty(saved_tool[0])

        ts_kernel = get_ts_dll()

        print("ts_kernel: ", ts_kernel)

        element_type = ts_kernel.GetType("TopSolid.Kernel.Automating.ElementId")

        print("element_type: ", element_type)

        element_id = clr.System.Activator.CreateInstance(element_type)

        print("element_id: ", element_id)
        print("element_id.id: ", element_id.DocumentId)
        
        print("tmp: ", tmp)
        
        name = ts_ext.Elements.SearchByName(tmp, "$TopSolid.Kernel.TX.Properties.Name")

        print("name: ", name)

        paramElementId = ts_ext.Elements.SearchByName(tmp, "D")

        print("paramElementId: ", paramElementId)
                    

        ts_ext.Parameters.SetRealValue(paramElementId, 0.002)



        ts_ext.Application.EndModification(True, False)

        ts_ext.Documents.Save(tmp)

        print("Tool parameters modified successfully!")
    except Exception as ex:
        ts_ext.Application.EndModification(False, False)
        print("Error modifying tool parameters: " + str(ex))
    finally:
        try:
            ts_ext.Application.EndModification(False, False)
        except Exception as ex:
            print("App closed -> modification end")





#opcao_selecionada = get_user_input()
opcao_selecionada = 1
# Mapear a opção selecionada para o nome da ferramenta correspondente
tool_type = None
if opcao_selecionada == 1:
    tool_type = "Side Mill"# D20 L35 SD20"
elif opcao_selecionada == 2:
    tool_type = "Radiused Mill D16 L40 r3 SD16"
elif opcao_selecionada == 3:
      tool_type = "Ball Nose Mill D8 L30 SD8"
elif opcao_selecionada == 4:
      tool_type = "Spotting Drill D10 SD10"
elif opcao_selecionada == 5:
      tool_type = "Twisted Drill D10 L35 SD10"
elif opcao_selecionada == 6:
      tool_type = "Constant Reamer D10 L20 SD9"
else:
    tool_type = "Side Mill D20 L35 SD20"


# Example usage: copy the "My Tool" tool
saved_tool = copy_tool(tool_type)

if saved_tool:
    print("saved: ", saved_tool)