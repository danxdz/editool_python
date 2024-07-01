import tkinter as tk
from tkinter import messagebox, Scrollbar, Listbox
from topsolid_api import TopSolidAPI

class TopSolidGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TopSolid Integration")
        self.geometry("800x600")

        self.topSolid = TopSolidAPI()

        self.project_list = []
        self.file_list = []

        # Frame for List and Checkboxes
        self.frame_list = tk.Frame(self)
        self.frame_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Listbox for Projects or Files
        self.listbox = tk.Listbox(self.frame_list)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Bind selection line event to Listbox
        self.listbox.bind("<<ListboxSelect>>", self.on_list_double_click)



        # Scrollbar for Listbox
        self.scrollbar_list = tk.Scrollbar(self.frame_list, command=self.listbox.yview)
        self.scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar_list.set)

        # Frame for Details Listbox
        self.frame_details = tk.Frame(self)
        self.frame_details.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Listbox for Project Details
        self.details_listbox = tk.Listbox(self.frame_details)
        self.details_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for Details Listbox
        self.scrollbar_details = tk.Scrollbar(self.frame_details, command=self.details_listbox.yview)
        self.scrollbar_details.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_listbox.config(yscrollcommand=self.scrollbar_details.set)

        # Frame for Checkboxes
        self.frame_checkboxes = tk.Frame(self)
        self.frame_checkboxes.pack(side=tk.TOP, fill=tk.X)

        # Checkboxes for Show All Projects and Show All Files
        self.show_all_projects = tk.BooleanVar()
        self.show_all_files = tk.BooleanVar()

        self.checkbox_projects = tk.Checkbutton(self.frame_checkboxes, text="Show All Projects", variable=self.show_all_projects, command=self.refresh_list)
        self.checkbox_projects.pack(side=tk.LEFT, padx=10)

        # Populate Listbox with Dummy Data
        self.populate_listbox()

    def populate_listbox(self):
        self.listbox.delete(0, tk.END)  # Clear existing items

        # Get items based on checkbox values
        if self.show_all_projects.get():
            all_items = self.topSolid.ts.Pdm.GetProjects(True, False)
        else:
            all_items = self.topSolid.get_open_projects()

        self.project_list = []

        for item in all_items:
            self.project_list.append(item)
        

        for item in self.project_list:
            self.listbox.insert(tk.END, f"{self.topSolid.get_name(item)} :: {item.Id}")
            #sort the list
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def refresh_list(self):
        self.populate_listbox()

    def on_list_double_click(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            item_name = self.listbox.get(selected_index)
            project_details = self.get_project_details(self.project_list[selected_index[0]])
            self.update_details_listbox(project_details)

    def get_project_details(self, project_name):
        try:
            project = self.topSolid.get_constituents(project_name, True)
            if project:
                # Example: Retrieving project details using TopSolidAPI
                project_details = []    
                for constituent in project:
                    print(f"Constituents in project: {len(project)}")
                    if not isinstance(constituent, list):
                        #project_details.append(f"Constituent: {self.topSolid.get_name(constituent)}")
                        print(f"Constituent: {self.topSolid.get_name(constituent)}")
                    else:
                        for sub_constituent in constituent:
                            if not isinstance(sub_constituent, str):
                                #const_type = self.topSolid.get_type(sub_constituent)
                                #if const_type != '':
                                #    consttype_1 = const_type[len(const_type)-1]
                                #else:
                                #    consttype_1 = "None"
                                project_details.append(f"{self.topSolid.get_name(sub_constituent)} ::") # {consttype_1}")

                            else:
                                project_details.append(f"{sub_constituent}")
                return project_details
            else:
                return [f"Project '{project_name}' not found."]
        except Exception as e:
            print(f"Error retrieving project details: {e}")
            return [f"Error: {e}"]



    def update_details_listbox(self, details):
        self.details_listbox.delete(0, tk.END)  # Clear existing items
        for detail in details:
            self.details_listbox.insert(tk.END, detail)

if __name__ == "__main__":
    app = TopSolidGUI()
    app.mainloop()
