import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Notebook
from pyglet import gl, shapes
from pyglet.window import Window, event, pyglet

import xml.etree.ElementTree as ET
import sqlite3

# Classe para a visualização 3D da ferramenta
class ToolPreview:
    def __init__(self):
        self.batch = shapes.Batch()
        self.shape = shapes.Circle(0, 0, 100, color=(255, 255, 255), batch=self.batch)
        self.window = None

    def create_window(self):
        config = pyglet.gl.Config(double_buffer=True)
        self.window = Window(config=config)
        self.window.on_resize = self.on_resize
        self.window.switch_to()
        self.window.dispatch_events()

    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-width/2, width/2, -height/2, height/2, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        return event.EVENT_HANDLED

    def render(self):
        if self.window is not None:
            self.window.switch_to()
            self.window.clear()
            self.batch.draw()

# Classe para o Gerenciador de Ferramentas
class ToolManagerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tool Manager")

        # Crie a barra de menu
        menubar = tk.Menu(self.root)

        # Crie o menu "Ferramenta"
        tool_menu = tk.Menu(menubar, tearoff=0)
        tool_menu.add_command(label="Nova Ferramenta", command=self.create_tool)
        tool_menu.add_command(label="Abrir XML", command=self.open_xml_file)
        tool_menu.add_command(label="Salvar Ferramenta", command=self.save_tool)
        tool_menu.add_separator()
        tool_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Ferramenta", menu=tool_menu)

        # Associe a barra de menu à janela principal
        self.root.config(menu=menubar)

        # Crie uma tab para a visualização 3D
        self.notebook = Notebook(self.root)
        self.preview_tab = tk.Frame(self.notebook)
        self.notebook.add(self.preview_tab, text="Visualização 3D")
        self.notebook.pack()

        # Crie a visualização 3D
        self.tool_preview = ToolPreview()
        self.tool_preview.create_window()
        self.tool_preview.render()

        self.root.after(100, self.update_tool_preview)

        self.root.mainloop()

    def open_xml_file(self):
        xml_file_path = askopenfilename(title='Selecione um arquivo XML', filetypes=[('XML Files', '*.xml')])
        if xml_file_path:
            self.extract_tool_data(xml_file_path)
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado.")

    def extract_tool_data(self, xml_file_path):
        # Extrai os dados da ferramenta do arquivo XML
        tool = self.parse_xml_data(xml_file_path)

        if tool is not None:
            # Exibe os dados da ferramenta
            self.display_tool_data(tool)
        else:
            messagebox.showwarning("Aviso", "Falha ao extrair os dados da ferramenta do arquivo XML.")

    def parse_xml_data(self, xml_file_path):
        paramToPropDict = {}

        with open('DIN4000.txt') as file:
            for line in file:
                fields = line.strip().split(';')
                if len(fields) > 2:
                    paramToPropDict[fields[0]] = fields[1]

        if xml_file_path:
            documentoXml = ET.parse(xml_file_path)
            xmlDoc = documentoXml.getroot()

            toolNode = xmlDoc.find('.//Tool')
            newTool = Tool()

            for categoryNode in toolNode.findall('.//Category-Data'):
                categoryName = categoryNode.find('PropertyName').text.strip()
                if categoryName == 'NSM':
                    nsmValue = categoryNode.find('Value').text.strip()
                    if nsmValue in paramToPropDict:
                        propName = paramToPropDict[nsmValue]
                        setattr(newTool, 'Type', propName)
                    break

            for node in toolNode:
                for paramNode in node.findall('Property-Data'):
                    paramName = paramNode.find('PropertyName').text.strip()
                    paramValue = paramNode.find('Value').text.strip()

                    if paramName in paramToPropDict:
                        propName = paramToPropDict[paramName]
                        prop = getattr(newTool, propName)
                        paramValue = paramValue.replace(',', '.')
                        if paramValue == 'FSA':
                            paramValue = 'FRAISA' #TODO check list to show right name

                        if paramValue.isdigit():
                            setattr(newTool, propName, int(paramValue))
                        else:
                            try:
                                setattr(newTool, propName, float(paramValue))
                            except ValueError:
                                setattr(newTool, propName, paramValue)

            return newTool
        else:
            return None

    def display_tool_data(self, tool):
        messagebox.showinfo("Dados da Ferramenta", f"Nome: {tool.Name}\nTipo: {tool.Type}\nD1: {tool.D1}\nD2: {tool.D2}")

    def create_tool(self):
        # Crie uma nova ferramenta
        pass

    def save_tool(self):
        # Salve os dados da ferramenta
        pass

    def update_tool_preview(self):
        # Atualize a visualização 3D da ferramenta com base nos dados fornecidos
        # Obtenha a ferramenta atualmente selecionada ou use a ferramenta criada
        # na função extract_tool_data() e atualize a visualização conforme necessário
        self.tool_preview.render()

# Inicialize o Gerenciador de Ferramentas
tool_manager_ui = ToolManagerUI()
