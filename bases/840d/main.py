from tkinter import Tk
from gui2 import NC_Debugger_GUI
from program_handler import ProgramHandler

if __name__ == "__main__":
    root = Tk()
    root.title("NC Debugger - Simulação de Canais")
    
    # Inicializa o manipulador de programa com canais separados
    program_handler = ProgramHandler()
    
    # Passa o handler para a GUI
    app = NC_Debugger_GUI(root, program_handler)
    
    root.mainloop()
