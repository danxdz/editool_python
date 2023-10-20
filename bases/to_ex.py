from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Cria a janela principal
root = Tk()
root.withdraw()  # Esconde a janela principal

# Abre a caixa de diálogo para selecionar um arquivo
file_path = askopenfilename()

# Verifica se um arquivo foi selecionado
if file_path:
    print("Arquivo selecionado:", file_path)
else:
    print("Nenhum arquivo selecionado")
