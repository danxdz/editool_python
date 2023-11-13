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
    
    import TopSolid.Kernel.Automating as Automating
    from TopSolid.Kernel.Automating import PrintColorMapping

    top_solid_kernel = Automating

    top_solid_kernel_type = top_solid_kernel.TopSolidHostInstance
    ts_ext = clr.System.Activator.CreateInstance(top_solid_kernel_type)

    top_solid_kernel_colors = top_solid_kernel.PrintColorMapping
    color_type = clr.System.Activator.CreateInstance(top_solid_kernel_colors)
    print ("TOP:: ", top_solid_kernel_colors, " : ",  color_type)

    # Connect to TopSolid
    ts_ext.Connect()

    #print connected with version
    print("TopSolid " + top_solid_version + " connected successfully!")
    all_projects = ts_ext.Pdm.GetProjects(True, False)
    
    global valid

    for proj in all_projects:
        proj_name = ts_ext.Pdm.GetName(proj)
        #print ("Project :: ",proj_name)
        cons = ts_ext.Pdm.GetConstituents(proj)

        valid = False
        for c in cons:
            for elem in c:
                elem_name = ts_ext.Pdm.GetName(elem)
                elem_type = ts_ext.Pdm.GetType(elem)

                if str(elem_type[0]) == "Folder":
                    if str(elem_name) == "DOCS":
                        valid = True
                        docs = ts_ext.Pdm.GetConstituents(elem)  
                        print("Folder Docs :: ")
                        if docs:                                
                            for doc in docs:
                                if doc:
                                    for d in doc:
                                        #print (d)
                                        doc_name = ts_ext.Pdm.GetName(d)
                                        print (doc_name)
                                        doc_id = ts_ext.Documents.GetDocument(d)
                                        print(doc_id)

                                        color_mapping = PrintColorMapping(0)
                                        
                                        print(f"Color {color_mapping}")

                                        tmp = int("1")
                                        res = str("name")
                                        #void ExportWithOptions(int inExporterIx, List<KeyValue> inOptions, DocumentId inDocumentId, string inFullName);
                                        list = [1,2,3]
                                        #export = ts_ext.Documents.ExportWithOptions(tmp,list,  doc_id, "123")
                                        #void Export(int inExporterIx, DocumentId inDocumentId, string inFullName);
                                        export = ts_ext.Documents.Export(1, doc_id, "123")
                                        #export = ts_ext.Documents.Print(doc_id,color_mapping,300)
                                        print (export)          
                #print ("Elem ::" , elem_name , "::" , elem_type[0], valid)
        print("Project:: ", proj_name , " :: ", valid )

    ts_ext.Disconnect()

except Exception as ex:
    # Handle
    print("error :: ", ex)
