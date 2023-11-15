import winreg
import os
import clr

from ts import get_ts_dll

key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

try:
   
    ts_ext = get_ts_dll()

    all_projects = ts_ext.Pdm.GetProjects(True, False)
    
    global valid

    for proj in all_projects:
        proj_name = ts_ext.Pdm.GetName(proj)
        #print ("Project :: ",proj_name)
        cons = ts_ext.Pdm.GetConstituents(proj)

        print("Project:: ", proj_name  )

        valid = False
        for c in cons:
            for elem in c:
                elem_name = ts_ext.Pdm.GetName(elem)
                elem_type = ts_ext.Pdm.GetType(elem)

                if str(elem_type[0]) == "Folder":
                    if str(elem_name) == "DOCS":
                        valid = True
                        docs = ts_ext.Pdm.GetConstituents(elem)  
                        if docs:                                
                            print("Folder Docs :: ")
                            export_path = os.getcwd() + "/pdf/ART " + proj_name + "/DOCS/"
                            res = os.makedirs(export_path)
                            for doc in docs:
                                if doc:
                                    for d in doc:
                                        doc_name = ts_ext.Pdm.GetName(d)
                                        print (doc_name)
                                        doc_id = ts_ext.Documents.GetDocument(d)
                                        
                                        #to print pdf
                                        #color_mapping = PrintColorMapping(0)
                                        #print(f"Color {color_mapping}")
                                        
                                        exporter_type = ts_ext.Application.GetExporterFileType(10,"outFile","outExt") #10 to pdf \ 8 step
                                        
                                        #print ("exporter_type")
                                        #print (exporter_type[0] , exporter_type[1][0])

                                        
                                        print("res", res)
                                        complete_path = export_path + "/" + doc_name + exporter_type[1][0]
                                        print(complete_path)

                                        

                                        export = ts_ext.Documents.Export(10, doc_id,complete_path) #10 pdf

                                        #exporter_options = ts_ext.Application.GetExporterOptions(10)
                                        #void ExportWithOptions(int inExporterIx, List<KeyValue> inOptions, DocumentId inDocumentId, string inFullName);
                                        #export = ts_ext.Documents.ExportWithOptions(10, exporter_options,  doc_id, doc_name) #10 pdf         

                #print ("Elem ::" , elem_name , "::" , elem_type[0], valid)

    ts_ext.Disconnect()

except Exception as ex:
    # Handle
    print("error :: ", ex)
