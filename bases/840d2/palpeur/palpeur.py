# -*- coding: utf-8 -*-
import os
import re

import tkinter as tk

from constants import BASE_PATH

from gui import NC_Debugger_GUI



# --- Main Execution (Simplified) ---
if __name__ == "__main__":
    # Ensure the base NC programs directory exists
    if not os.path.exists(BASE_PATH):
        try:
            os.makedirs(BASE_PATH)
            print(f"Created directory: {BASE_PATH}")
            print(f"NOTE: Please ensure required NC files (BP*.nc) are present in '{BASE_PATH}'.")
        except Exception as e:
            print(f"Error creating base path '{BASE_PATH}': {e}")
            exit()

    # Start the GUI application
    print("Starting GUI...")
    root = tk.Tk()
    gui = NC_Debugger_GUI(root)
    root.mainloop()