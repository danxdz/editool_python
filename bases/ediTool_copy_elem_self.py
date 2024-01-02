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

    import TopSolid.Kernel.Automating as Automating

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
        # find model tool to copy from default lib
        #output_lib = ts_ext.Pdm.SearchProjectByName("Tool Lib")
        output_lib = ts_ext.Pdm.GetCurrentProject()

        toolModelId = ts_ext.Pdm.SearchDocumentByName(modelLib[0], toolModel)

        firstTool = toolModelId[0]
        toolModelId.Clear()
        toolModelId.Add(firstTool)

        print("toolModelId: ", toolModelId[0].Id)


        savedTool = ts_ext.Pdm.CopySeveral(toolModelId, output_lib)

        print("savedtool: ",savedTool[0].Id)
        print(f"Tool copied successfully!")

        # print("savedTool: ", ts_ext.Documents.Save(tmp))
        #ts_ext.Documents.Open(tmp)

        modif = ts_ext.Application.StartModification("tmp", True)
        print("Start modif: ", modif)
        
        savedToolDocId = ts_ext.Documents.GetDocument(savedTool[0])
        print("savedToolDocId.PdmDocumentId: ", savedToolDocId.PdmDocumentId)
        savedToolModif = ts_ext.Documents.EnsureIsDirty(savedToolDocId)
        print("savedToolModif.PdmDocumentId: ", savedToolModif.PdmDocumentId)

        ts_kernel = get_ts_dll()

        nameType = ts_kernel.ElementId

        name = ts_ext.Elements.SearchByName(savedToolModif, "$TopSolid.Kernel.TX.Properties.Name")
        name = ts_ext.Parameters.SetTextParameterizedValue(name, "FR 2T D[D]")

        Nott = ts_ext.Parameters.SetIntegerValue(ts_ext.Elements.SearchByName(savedToolModif, "NoTT"), 2)
 
        d1 = ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"D"), 0.010)
        d2 = ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"CTS_ED"), 0.0098)
        d3 = ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"SD"), 0.010)
        l1 = ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"L"), 0.02)
        l2 = ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"CTS_EL"), 0.03)
        l3 = ts_ext.Parameters.SetRealValue(ts_ext.Elements.SearchByName(savedToolModif,"OL"), 0.05)

        #ts_ext.Application.EndModification(True, False)
        EndModif(True, False)

        ts_ext.Documents.Open(savedToolModif)
        #ts_ext.Documents.Save(dirty)

    except Exception as ex:
        EndModif(False,False)

        print("Error copying tool: " + str(ex))

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
        print("Error modifying tool parameters: " + str(ex))
    finally:
        try:
            ts_ext.Application.EndModification(False, False)
        except Exception as ex:
            print("App closed -> modification end")





#testing 
#to show all types
def list_properties_methods():
    ts_dll = get_ts_dll()
    if ts_dll is None:
        # Handle error
        return None

    # Get the TopSolid.Kernel.Part class
    part_type = ts_dll.GetType("TopSolid.Kernel.Part")

    for t in ts_dll.GetTypes():
        print(t.FullName)

list_properties_methods()
exit()

opcao_selecionada = get_user_input()

# Mapear a opção selecionada para o nome da ferramenta correspondente
tool_type = None
if opcao_selecionada == 1:
    tool_type = "Side Mill D20 L35 SD20"
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