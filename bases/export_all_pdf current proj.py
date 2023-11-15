import winreg
import os
import clr

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
    # *************************
    top_solid_kernel_path = os.path.join(
    top_solid_path, "bin", "TopSolid.Kernel.Automating.dll")
    print(f"Loading dll: {top_solid_kernel_path}")
    clr.AddReference(top_solid_kernel_path)

    #set preload to true to load all dependent dlls
    clr.setPreload(True)
    #see all loaded assemblies
    #print( clr.__dict__)
    
    import TopSolid.Kernel.Automating as Automating
    from TopSolid.Kernel.Automating import PrintColorMapping
    from TopSolid.Kernel.Automating import KeyValue
    from TopSolid.Kernel.Automating import TopSolidHostInstance
    from TopSolid.Kernel.Automating import PdmObjectId
    
    

    #for member_name in dir(TopSolidHostInstance.get_Licenses):
        #print(member_name)
    
    

    top_solid_kernel = Automating

    #list all members of the module
    #for member_name in dir(Automating):
    #    print(member_name)



    # Obtém todos os membros do objeto
    """   members = dir(Automating.IDocuments)

        # Itera sobre cada membro
        for member_name in members:
            # Obtém o valor do membro
            member_value = getattr(Automating.IDocuments, member_name)
            
            print(f'Membro: {member_name}')
            
            # Verifica se é um método
            if callable(member_value):
                print(f'Tipo: Método')
            else:
                print(f'Tipo: Propriedade ou Atributo')
            
            # Tenta obter a documentação do membro
            docstring = getattr(member_value, '__doc__', None)
            if docstring:
                print(f'Docstring: {docstring.strip()}')
            
            print('-' * 40)
    """


    top_solid_kernel_type = top_solid_kernel.TopSolidHostInstance
    ts_ext = clr.System.Activator.CreateInstance(top_solid_kernel_type)

    top_solid_kernel_colors = top_solid_kernel.PrintColorMapping
    color_type = clr.System.Activator.CreateInstance(top_solid_kernel_colors)
 
    # Connect to TopSolid
    ts_ext.Connect()

    #print connected with version
    print("TopSolid " + top_solid_version + " connected successfully!")

    current_project = ts_ext.Pdm.GetCurrentProject()

    proj_name = ts_ext.Pdm.GetName(current_project)
    
    print("Current project:: ", proj_name  )

    export_path = os.getcwd() + "/pdf/ART " + proj_name + "/"

    try:
        res = os.makedirs(export_path)
    except Exception as ex:
        # Handle
        print("error :: ", ex)
        pass
    
    proj_const = ts_ext.Pdm.GetConstituents(current_project)

    for const in proj_const:
        for elem in const:
            elem_name = ts_ext.Pdm.GetName(elem)
            print ("elem_name ::" , elem_name)
            elem_type = ts_ext.Pdm.GetType(elem)
            print ("elem_type ::" , elem_type[0])

           

            if str(elem_type[0]) == "Folder":
                if str(elem_name) == "DOCS":
                 
                    valid = True
                    docs = ts_ext.Pdm.GetConstituents(elem)  
                    if docs:                                
                        print("Folder Docs :: ")
                        
                        export_path_docs = export_path + "/DOCS/"
                        
                        try:
                            res = os.makedirs(export_path_docs)
                        except Exception as ex:
                            # Handle
                            print("error :: ", ex)
                            pass
                        
                        for doc in docs:
                            if doc:
                                for d in doc:
                                    doc_type = ts_ext.Pdm.GetType(d)
                                    print ("doc_type ::" , doc_type[1])
                                    if str(doc_type[1]) == ".TopDft":#".TopPrt":#
                                        doc_name = ts_ext.Pdm.GetName(d)
                                        print ("doc_name ::" , doc_name)
                                        doc_id = ts_ext.Documents.GetDocument(d)
                                        
                                        #to print pdf
                                        color_mapping = PrintColorMapping(0)
                                        #print(f"Color {color_mapping}")
                                        
                                        exporter_type = ts_ext.Application.GetExporterFileType(10,"outFile","outExt") #10 to pdf \ 8 step
                                        ts_ext.Documents.Open(doc_id)
                                        ts_ext.Documents.Close(doc_id, False, False)
                                        ts_ext.Documents.Save(doc_id)
                                        ts_ext.Pdm.CheckIn(d,True)
                                        check = ts_ext.Pdm.GetLifeCycleMainState(d)
                                        print ("check ::" , check)  

                                        #docs_to_update = ts_ext.Documents.GetReferencedDocuments(doc_id,True)
                                        #print("GetReferencedDocuments :: ", docs_to_update)
                                        #for d in docs_to_update:
                                        #    print("GetReferencedDocuments :: ", d)
                                        #    print("GetName :: ", ts_ext.Documents.GetName(d))


                                        #print ("exporter_type")
                                        #print (exporter_type[0] , exporter_type[1][0])
                                        #ts_ext.Documents.Print(doc_id, color_mapping, 300)                                           
                                


                                        complete_path = export_path_docs + "/" + doc_name + exporter_type[1][0]
                                        export = ts_ext.Documents.Export(10, doc_id,complete_path) #10 pdf


                                        #exporter_options = ts_ext.Application.GetExporterOptions(10)
                                        #void ExportWithOptions(int inExporterIx, List<KeyValue> inOptions, DocumentId inDocumentId, string inFullName);
                                        #export = ts_ext.Documents.ExportWithOptions(10, exporter_options,  doc_id, doc_name) #10 pdf         

                #print ("Elem ::" , elem_name , "::" , elem_type[0], valid)
            else:
                try:
                    elem_docId = ts_ext.Documents.GetDocument(elem)
                    print ("elem_docId ::" , elem_docId)
                    elem_type = ts_ext.Pdm.GetType(elem)
                    print ("elem_type ::" , elem_type[1])
                    elem_name = ts_ext.Documents.GetName(elem_docId)
                    print ("elem_name ::" , elem_name)
                    ts_ext.Documents.Open(elem_docId)
                    ts_ext.Documents.Close(elem_docId, False, False)
                    ts_ext.Documents.Save(elem_docId)
                    ts_ext.Pdm.CheckIn(elem,True)
                    check = ts_ext.Pdm.GetLifeCycleMainState(elem)
                    print ("check ::" , check)  
                except Exception as ex:
                    # Handle
                    print("error :: ", ex)
                    pass



    #Sub CheckIn(inObjectId As TopSolid.Kernel.Automating.PdmObjectId) Membre de TopSolid.Kernel.Automating.IPdm

    #create a system generiv list of projects
    proj_list = clr.System.Collections.Generic.List[PdmObjectId]()
    proj_list.Add(current_project)
    pkg = export_path + proj_name +".TopPkg"
    res = ts_ext.Pdm.ExportPackage(proj_list, False, False, pkg )
    print ("res ::" , res)

    ts_ext.Disconnect()

except Exception as ex:
    # Handle
    print("error :: ", ex)
