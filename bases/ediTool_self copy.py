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
