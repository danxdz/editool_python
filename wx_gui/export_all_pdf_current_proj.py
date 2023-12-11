import winreg
import os
import clr
import json

import ts


key_path = "SOFTWARE\\TOPSOLID\\TopSolid'Cam"

global json_data 
global export_path

json_data = {}


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


def getType(obj):
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
        ts_type = str(ts_ext.Documents.GetType(obj)[0])
    #print ("getType :: res obj_type :: ::" , ts_type)
    return ts_type


def getName(obj): #get element name - PdmObjectId or DocumentId
    #get python object type
    obj_type = type(obj)
    #print ("name obj_type ::" , obj_type)
    if obj_type is PdmObjectId:
        name = str(ts_ext.Pdm.GetName(obj))
    elif obj_type is DocumentId:
        name = str(ts_ext.Documents.GetName(obj))
    #print ("get name ::" , name)
    return name
    

def check_files(pdmId,pdm_type,export_path_docs):
    print ("check_files ::" , pdmId , "::" , pdm_type, "::" , export_path_docs)

    if str(pdm_type) != "UnknownDocument":
        #".TopDft"
        doc_id = ts_ext.Documents.GetDocument(pdmId)

        """
        MRev = ts_ext.Pdm.GetLastMajorRevision(pdmId)
        mRev = ts_ext.Pdm.GetLastMinorRevision(MRev)
        updateRef = ts_ext.Pdm.UpdateDocumentReferences(mRev)

        lastRev = ts_ext.Pdm.NeedsGettingLatestRevision(pdmId)

        needUpdate = ts_ext.Pdm.NeedsUpdating(pdmId)

        needRefresh = ts_ext.Documents.NeedsRefreshing(doc_id)

        canExport = ts_ext.Documents.CanExport(10,doc_id)#10=pdf

        state = ts_ext.Pdm.GetState(pdmId)
        """

        #ts_ext.Documents.Open(doc_id)
        #ts_ext.Documents.Close(doc_id, True, False)
        #ts_ext.Documents.Save(doc_id)
        #ts_ext.Pdm.CheckIn(pdmId,True)
        #get global export path_docs

        doc_type = getType(pdmId)
        print ("doc_type ::" , doc_type)
        if doc_type == ".TopDft":#".TopPrt":#
            doc_name = ts_ext.Pdm.GetName(pdmId)
            print ("doc_name ::" , doc_name)

            make_path(export_path_docs)

            exporter_type = ts_ext.Application.GetExporterFileType(10,"outFile","outExt") #10 to pdf \ 8 step

            #complete_path = export_path_docs + "/" + doc_name + exporter_type[1][0]
            complete_path = os.path.join(export_path_docs, f"{doc_name}{exporter_type[1][0]}")
            
            export = ts_ext.Documents.Export(10, doc_id,complete_path) #10 pdf


def search_folder(elem, export_path_docs):
    print("search_folder ::", elem, "::", export_path_docs)
    const = ts_ext.Pdm.GetConstituents(elem)  # get all elements in folder
    print("docs ::", len(const))
    
    folderName = getName(elem)
    new_export_path_docs = os.path.join(export_path_docs, folderName)
   
    files_list = []

    for pdmIdList in const:
        if pdmIdList:
            num = str(len(pdmIdList))
            print(num)
            for pdmId in pdmIdList:
                pdm_type = getType(pdmId)
                pdm_name = getName(pdmId)
                out = pdm_name + " ;; " + pdm_type
                print(out)
                pdm = {}
                pdm["name"] = pdm_name
                pdm["type"] = pdm_type
                files_list.append(pdm)

                if pdm_type == "Folder":
                    search_folder(pdmId, new_export_path_docs)
                else:
                    check_files(pdmId, pdm_type, new_export_path_docs)

    if len(files_list) > 0:
        print("files_list ::", files_list)
        write_json(folderName, files_list)

def GetConstituents(folder, export_path_docs):
    folder_const = ts_ext.Pdm.GetConstituents(folder)
    folder_name = getName(folder)
    export_path_docs += folder_name + "/"

    printFolder(folder_const, folder_name,export_path_docs)
    write_json(folder_name, "dir")
    #print ("make path ::" , folder_const,  " :: " , folder_name, " : : ",  export_path_docs)

    for file in folder_const[1]:
        printInfo(file, "::")
        print("select case type ::", getType(file))
        if getType(file) == ".TopDft":
            make_path(export_path_docs)
            export_pdf(file, export_path_docs)
        
    for dir in folder_const[0]:
        GetConstituents(dir, export_path_docs)


def export_pdf(file, export_path_docs):
    doc_name = ts_ext.Pdm.GetName(file)
    doc_id = ts_ext.Documents.GetDocument(file)                
    exporter_type = ts_ext.Application.GetExporterFileType(10,"outFile","outExt") #10 to pdf \ 8 step
    ts_ext.Documents.Open(doc_id)
    ts_ext.Documents.Close(doc_id, False, False)
    ts_ext.Documents.Save(doc_id)
    ts_ext.Pdm.CheckIn(file,True)

    complete_path = export_path_docs + "/" + doc_name + exporter_type[1][0]
    ts_ext.Documents.Export(10, doc_id,complete_path) #10 pdf
    print ("exported pdf ::" , doc_name)        

def printInfo (file, msg):
    file_name = getName(file)
    file_type = getType(file)
    print (msg , " ; ", file_name , " ; " ,file_type )
    write_json(file_name, file_type)


def printFolder (folder_const, folder_name, export_path_docs):
    if len(folder_const[0])>0 or len(folder_const[1])>0:
        print (str("dir " + folder_name + " @ " + export_path_docs + " have "), end="")
        if len(folder_const[0])>0:
            print (str(len(folder_const[0])) + " folders ",end="")
        if len(folder_const[1])>0:
            print (str(len(folder_const[1])) + " files")
        else:
            print ("")
    else:
        print ("dir " + folder_name + " is empty")

#script start
#****************************************************************************************

prefix = "\ART "


try:
    #get topsolid API
    ts_ext = ts.connect()
    
    #get topsolid types
    from TopSolid.Kernel.Automating import PdmObjectId
    from TopSolid.Kernel.Automating import DocumentId

    current_project = ts_ext.Pdm.GetCurrentProject()
    current_proj_name = getName(current_project)

    export_path = os.getcwd() + prefix + current_proj_name + "/"

    write_json("project : " , current_proj_name)
    write_json("export_path : " , export_path)
    make_path(export_path)

    #state = ts_ext.Pdm.GetLifeCycleMainState(current_project)
    #print ("state ::" , state)
    
    proj_const = ts_ext.Pdm.GetConstituents(current_project)
    print ((str(len(proj_const[0])-1) + " folders in root project, "),end="")# -1 we don't want to count MODELES folder
    print (str(len(proj_const[1])) + " files in root project")
    
    for file in proj_const[1]:
        printInfo(file , "files")
        if getType(file) == ".TopDft":
            export_pdf(file, export_path)
        write_json(getName(file), getType(file))

    for folder in proj_const[0]:
            if getName(folder) == "Modèles":
                pass
            else:
                GetConstituents(folder, export_path)


    
    print(json_data)

    with open('data.json', 'w') as outfile:
        #format json
        #print("json_data :: ", json_data)
        json_data = json.dumps(json_data, indent=4, sort_keys=False)
        #print("json_data :: ", json_data)
        outfile.write(json_data)
    
    ts_ext.Disconnect()
    
    exit()

except Exception as ex:
    # Handle
    print("error :: ", ex)
