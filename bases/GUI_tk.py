import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Notebook, Label, Treeview
import sqlite3
from tool import Tool
from import_xml import open_xml_file

from tool_preview import ToolPreview

# Classe para o Gerenciador de Ferramentas
class ToolManagerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tool Manager")
        self.geometry("800x600")

        # Cria uma barra de menu
        menubar = tk.Menu(self)

        # Cria o menu "Ferramenta"
        tool_menu = tk.Menu(menubar, tearoff=0)
        tool_menu.add_command(label="Nova Ferramenta", command=self.create_tool)
        tool_menu.add_command(label="Abrir XML", command=self.open_xml_file)
        tool_menu.add_command(label="Salvar Ferramenta", command=self.save_tool)
        tool_menu.add_separator()
        tool_menu.add_command(label="Sair", command=self.quit)
        menubar.add_cascade(label="Ferramenta", menu=tool_menu)

        self.config(menu=menubar)

        # Cria um notebook para exibir as guias
        self.notebook = Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Cria uma guia para a visualização 3D
        self.preview_tab = tk.Frame(self.notebook)
        self.notebook.add(self.preview_tab, text="Visualização 3D")

        # Cria a visualização 3D
        self.tool_preview = ToolPreview(self.preview_tab)
        self.tool_preview.pack(fill=tk.BOTH, expand=True)

        # Cria um Label para exibir os dados da ferramenta
        self.tool_data_label = Label(self, text="")
        self.tool_data_label.pack(side=tk.BOTTOM)

        # Cria o Treeview para exibir as ferramentas
        self.tool_treeview = Treeview(self, columns=("type", "d1", "d2"))
        self.tool_treeview.heading("#0", text="Nome")
        self.tool_treeview.heading("type", text="Tipo")
        self.tool_treeview.heading("d1", text="D1")
        self.tool_treeview.heading("d2", text="D2")
        self.tool_treeview.pack(fill=tk.BOTH, expand=True)
        
        self.tool_treeview.bind("<<TreeviewSelect>>", self.on_tool_select)

        # Lê as ferramentas do banco de dados e adiciona ao Treeview
        self.load_tools_from_database()

    def update_tool_list(self):
        # Limpa o Treeview
        self.tool_treeview.delete(*self.tool_treeview.get_children())
        print("Ferramentas atualizadas.")
        # Recarrega as ferramentas do banco de dados
        self.load_tools_from_database()

    def open_xml_file(self):
        tool = open_xml_file()
        print("Ferramenta lida do arquivo XML: ", tool)
        # Exibe os dados da ferramenta
        self.display_tool_data(tool)
        self.add_tool_to_treeview(tool)
        
            

    def display_tool_data(self, tool):
        # Exibe os dados da ferramenta no Label
        print("Display tool label: ", tool.Name)
        tool_data = f"Nome: {tool.Name}\nTipo: {tool.Type}\nD1: {tool.D1}\nD2: {tool.L1}"
        self.tool_data_label.config(text=tool_data)

    def create_tool(self):
        # Crie uma nova ferramenta
        pass

    def save_tool(self):
        # Salve os dados da ferramenta
        pass

    def load_tools_from_database(self):
        # Conecta ao banco de dados
        conn = sqlite3.connect('tool_manager.db')
        cursor = conn.cursor()

        # Lê as ferramentas do banco de dados
        cursor.execute("SELECT * FROM tools")
        tools = cursor.fetchall()
        print("Ferramentas lidas do banco de dados: ", tools.__len__())
        # Adiciona as ferramentas ao Treeview
        for tool_data in tools:
            # Exclua o primeiro elemento (id) dos dados da ferramenta
            tool = Tool(*tool_data[1:])
            self.add_tool_to_treeview(tool)
        # Fecha a conexão com o banco de dados
        conn.close()


    def add_tool_to_treeview(self, tool):
        print("Add tool to treeview: ", tool.Name)
        self.tool_treeview.insert("", "end", text=tool.Name, values=(tool.Type, tool.D1, tool.D2))

    def on_tool_select(self, event):
        # Obtém o item selecionado no Treeview
        selected_item = self.tool_treeview.selection()

        # Verifica se um item foi selecionado
        if selected_item:
            # Obtém os valores da ferramenta selecionada
            values = self.tool_treeview.item(selected_item)["values"]

            # Cria uma nova instância da classe Tool com os dados disponíveis
            tool = Tool(Type=values[0], D1=values[1], D2=values[2])

            # Atualiza o Label com os dados da ferramenta selecionada
            tool_data = f"Tipo: {values[0]}\nD1: {values[1]}\nD2: {values[2]}"
            self.tool_data_label.config(text=tool_data)
            self.tool_preview.set_tool_data(tool)


if __name__ == "__main__":
    tool_manager_ui = ToolManagerUI()
    tool_manager_ui.mainloop()
