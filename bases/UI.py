import tkinter as tk
from tkinter import messagebox

class ToolManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Ferramentas")
        
        # Criar widgets da interface gráfica
        self.label = tk.Label(self, text="Bem-vindo ao Gestor de Ferramentas!")
        self.label.pack(pady=10)
        
        self.add_button = tk.Button(self, text="Adicionar Ferramenta", command=self.open_add_tool_window)
        self.add_button.pack(pady=5)
        
        self.view_button = tk.Button(self, text="Visualizar Ferramentas", command=self.view_tools)
        self.view_button.pack(pady=5)
        
    def open_add_tool_window(self):
        # Lógica para abrir uma nova janela para adicionar uma ferramenta
        messagebox.showinfo("Adicionar Ferramenta", "Janela de adicionar ferramenta aberta.")
        
    def view_tools(self):
        # Lógica para exibir as ferramentas existentes
        messagebox.showinfo("Visualizar Ferramentas", "Ferramentas disponíveis: Ferramenta 1, Ferramenta 2, Ferramenta 3.")
        print(messagebox.askokcancel("rrr","rrrr"))


# Executar o aplicativo
app = ToolManagerApp()
app.mainloop()
