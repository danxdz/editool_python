from topsolid_api import TopSolidAPI

def main():
    # Criar uma instância da classe TopSolidAPI
    with TopSolidAPI() as topSolid:
        
        # get the current project library and name
        lib, name = topSolid.get_current_project()
        print(lib, name)
   
        # get the object type of the current project
        lib_type = lib.GetType() 
        print(lib_type)

        # get the current project constituents
        lib_const = topSolid.get_constituents(lib, False)
        print(lib_const)

        # open all the constituents of the current project
        #for i in lib_const:
        #    topSolid.open_file(i)

        topSolid.check_in_all(lib_const)
        
        # get the current project library and name
        
        files = topSolid.get_open_files()
        print(type(files), len(files))
        if type(files) == 'TopSolid.Kernel.Automating.DocumentId':
            topSolid.ask_plan(files)
        else:
            for f in files:
                print(f)
                topSolid.open_file(f)
                topSolid.ask_plan(f)


        print(topSolid.design.IsConnected)




if __name__ == "__main__":
    main()
