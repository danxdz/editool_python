import os

def list_files_in_dir():
    # Prompt the user for a directory
    dir_path = input("Please enter the path to the directory: ")
    
    # Verify the directory exists
    if not os.path.isdir(dir_path):
        print(f"The path '{dir_path}' is not a valid directory.")
        return

    # Get a list of all files in the directory
    try:
        file_names = os.listdir(dir_path)
    except Exception as e:
        print(f"An error occurred while reading the directory: {e}")
        return

    # Filter out directories, keep only files
    files_only = [f for f in file_names if os.path.isfile(os.path.join(dir_path, f))]
    
    # Write the file names to 'file_list.txt'
    output_file = "file_list.txt"
    try:
        with open(output_file, "w") as f:
            for file_name in files_only:
                f.write(file_name + "\n")
        print(f"File names have been written to '{output_file}'.")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

# Run the function
if __name__ == "__main__":
    list_files_in_dir()
