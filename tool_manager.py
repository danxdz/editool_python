import sqlite3
from PyQt5.QtWidgets import  QApplication, QMainWindow, QTextEdit, QAction, QDialog, QVBoxLayout, QPushButton, QDialogButtonBox, QDialog, QMenu, QMainWindow, QVBoxLayout, QWidget, QLabel, QTreeView, QAction, QFileDialog, QAbstractItemView,QPushButton,QMessageBox, QTextEdit

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from tool import Tool
from import_xml import open_xml_file
from import_past import interpret_tool_data
import ediTool
from export_xml import create_xml_data
from login import Ui_Dialog

from savebd import saveTool

debug = False

class PasteDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.text_edit = QTextEdit()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        self.button_box = QDialogButtonBox()
        self.button_box.addButton(self.ok_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        # Conectar os sinais dos botões aos slots adequados
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class ToolManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = self.tr("Tool Manager")
        self.width = 800
        self.height = 600

        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)

        self.login_dialog = None
        
        self.init_menu()
        self.init_ui()
        self.init_database()
        

    def init_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open XML", self)
        open_action.triggered.connect(self.open_xml_file)
        file_menu.addAction(open_action)

        open_action = QAction("Paste 13999 iso data", self)
        open_action.triggered.connect(self.iso_paste13999)
        file_menu.addAction(open_action)

        export_action = QAction("Export XML", self)
        export_action.triggered.connect(self.export_xml_file)
        file_menu.addAction(export_action)


        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.tool_data_label = QLabel()
        self.tool_data_label.setStyleSheet("QLabel { background-color: white; border: 1px solid gray; padding: 10px; }")

        layout.addWidget(self.tool_data_label)

        self.tool_create_btn = QPushButton()
        self.tool_create_btn.setText("Create Tool")
        self.tool_create_btn.setFixedWidth(100)
        self.tool_create_btn.setStyleSheet("QPushButton { background-color: white; border: 1px solid gray; padding: 10px; }")
        self.tool_create_btn.clicked.connect(self.on_button_clicked)
        layout.addWidget(self.tool_create_btn)

        self.tool_login_btn = QPushButton()
        self.tool_login_btn.setText("Login")
        self.tool_login_btn.setFixedWidth(100)
        self.tool_login_btn.setStyleSheet("QPushButton { background-color: white; border: 1px solid gray; padding: 10px; }")
        self.tool_login_btn.clicked.connect(self.on_login_click)
        layout.addWidget(self.tool_login_btn)

        self.tool_treeview = QTreeView()
        self.tool_treeview.setHeaderHidden(False)
        self.tool_treeview.setRootIsDecorated(True)  
        self.tool_treeview.clicked.connect(self.on_tool_select)
        
        self.tool_treeview.setContextMenuPolicy(Qt.CustomContextMenu)  # add context menu to treeview 
        self.tool_treeview.customContextMenuRequested.connect(self.show_context_menu) 

        self.tool_treeview.setSelectionMode(QAbstractItemView.SingleSelection)

        layout.addWidget(self.tool_treeview)

        # Create the model for the tree view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Type", "D1", "D2", "L1", "Manuf"])
        self.tool_treeview.setModel(self.model)

        self.tool_treeview.setColumnWidth(0, 200)  # Define a largura da primeira coluna
        self.tool_treeview.setColumnWidth(1, 100)  # Define a largura da segunda coluna
        self.tool_treeview.setColumnWidth(2, 100)  # Define a largura da terceira coluna
        self.tool_treeview.setColumnWidth(3, 100)  # Define a largura da quarta coluna
        self.tool_treeview.setColumnWidth(4, 100)  # Define a largura da quinta coluna
        self.tool_treeview.setColumnWidth(5, 100)  # Define a largura da sexta coluna

    def on_login_click(self):
        if not self.login_dialog or not self.ui:
            self.login_dialog = QDialog(self)
            self.ui = Ui_Dialog()
            self.ui.setupUi(self.login_dialog)
        self.login_dialog.show()



    def show_context_menu(self, pos):
            # Criar o menu de contexto
        context_menu = QMenu(self)

        # Adicionar ações ao menu de contexto
        action1 = context_menu.addAction("Opção 1")
        action2 = context_menu.addAction("Opção 2")

        # Conectar as ações aos métodos correspondentes
        action1.triggered.connect(self.action1_triggered)
        action2.triggered.connect(self.action2_triggered)

        # Exibir o menu de contexto na posição clicada
        context_menu.exec_(self.tool_treeview.mapToGlobal(pos))
    
    def action1_triggered(self):
        print("Opção 1 selecionada")

    def action2_triggered(self):
        print("Opção 2 selecionada")


    #handle button click
    def on_button_clicked(self):
        selected_index = self.tool_treeview.currentIndex()
        if selected_index.isValid():
            item = self.model.itemFromIndex(selected_index)
            tool = item.data(Qt.UserRole)  # Recupera o objeto Tool do item de dados
            if debug: print("Ferramenta selecionada: ", tool)
            if tool:
                # Faça o que desejar com a ferramenta selecionada
                saved_tool = ediTool.copy_tool(tool)
                print("Ferramenta copiada: ", saved_tool)
        else:
            QMessageBox.warning(self, "Seleção de Ferramenta", "Nenhuma ferramenta selecionada. Por favor, selecione uma ferramenta na lista.")

    #handle export xml file
    def export_xml_file(self):
        selected_index = self.tool_treeview.currentIndex()
        if selected_index.isValid():
            item = self.model.itemFromIndex(selected_index)
            tool = item.data(Qt.UserRole)
            print("Ferramenta selecionada: ", tool)
            if tool:
                # Faça o que desejar com a ferramenta selecionada
                xml_data = create_xml_data(tool)
                print("Ferramenta exportada: ", xml_data)
        else:
            QMessageBox.warning(self, "Seleção de Ferramenta", "Nenhuma ferramenta selecionada. Por favor, selecione uma ferramenta na lista.")




    def init_database(self):
        # Connect to the SQLite database
        self.conn = sqlite3.connect('tool_manager.db')
        self.cursor = self.conn.cursor()

        # Load tools from the database
        self.load_tools_from_database()


    def open_xml_file(self):
        tool = open_xml_file()
        if tool is not None:
            print("Ferramenta lida do arquivo XML: ", tool)
            # Exibe os dados da ferramenta
            self.display_tool_data(tool)
            self.add_tool_to_treeview(tool)



    def iso_paste13999(self):
        # Criar uma instância do diálogo personalizado
        dialog = PasteDialog()

        # Exibir o diálogo e verificar se o usuário pressionou "Ok"
        result = dialog.exec_()

        # Se o usuário pressionar "Ok", processar o texto colado
        if result == QDialog.Accepted:
            input_data = dialog.text_edit.toPlainText()
            result = interpret_tool_data(input_data)

            saveTool(result)
            self.display_tool_data(result)
            self.add_tool_to_treeview(result)

            # Agora você pode fazer o que quiser com o resultado, como exibir em outro widget, gravar em um arquivo, etc.
            print(result)


    def display_tool_data(self, tool):
        # Exibe os dados da ferramenta no Label
        tool_data = f"Name: {tool.Name}\nType: {tool.Type}\nD1: {tool.D1}\nL1: {tool.L1}\nManuf: {tool.Manuf}"
        self.tool_data_label.setText(tool_data)


    def add_tool_to_treeview(self, tool):
        if debug:print("Adicionando ferramenta ao Treeview: ", tool.D1, tool.L1, tool.Manuf, tool.Name, tool.Type)

        parent_item = QStandardItem(str(tool.Name))

        type_item = QStandardItem(str(tool.Type))
        d1_item = QStandardItem(str(tool.D1))
        d2_item = QStandardItem(str(tool.D2))
        l1_item = QStandardItem(str(tool.L1))
        manuf_item = QStandardItem(str(tool.Manuf))

        #parent_item.appendRow([type_item, d1_item, d2_item, l1_item, manuf_item])

        self.model.appendRow([parent_item,type_item, d1_item, d2_item, l1_item, manuf_item])

        parent_item.setData(tool, Qt.UserRole)  # Armazena o objeto Tool como item de dados
        type_item.setData(tool, Qt.UserRole)  # Armazena o objeto Tool como item de dados
        d1_item.setData(tool, Qt.UserRole)  # Armazena o objeto Tool como item de dados
        d2_item.setData(tool, Qt.UserRole)  # Armazena o objeto Tool como item de dados
        l1_item.setData(tool, Qt.UserRole)  # Armazena o objeto Tool como item de dados
        manuf_item.setData(tool, Qt.UserRole)  # Armazena o objeto Tool como item de dados


    def load_tools_from_database(self):
        # Lê as ferramentas do banco de dados
        self.cursor.execute("SELECT * FROM tools")
        tools = self.cursor.fetchall()
        print("Ferramentas lidas do banco de dados: ", len(tools))
        # Adiciona as ferramentas ao Treeview
        for tool_data in tools:
            tool = Tool(*tool_data[1:])
            self.add_tool_to_treeview(tool)

    def on_tool_select(self, index):
        item = self.model.itemFromIndex(index)
        tool = item.data(Qt.UserRole)  # Recupera o objeto Tool do item de dados
        print("Ferramenta selecionada: ", tool)
        if tool:
            # Acesse os parâmetros da ferramenta através do objeto Tool
            tool_data = f"Type: {tool.Type}\nD1: {tool.D1}\nL1: {tool.L1}"
            self.tool_data_label.setText(tool_data)


    def closeEvent(self, event):
        # Close the database connection when closing the application
        self.conn.close()
