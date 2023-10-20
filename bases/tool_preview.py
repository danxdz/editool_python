import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTreeView, QFrame, QAction, QFileDialog, QTreeWidgetItem, QAbstractItemView, QMenu, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from tool import Tool
from import_xml import open_xml_file

class ToolManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Tool Manager"
        self.width = 800
        self.height = 600

        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)

        self.init_menu()
        self.init_ui()

    def init_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open XML", self)
        open_action.triggered.connect(self.open_xml_file)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def init_ui(self):
        self.tool_data_label = QLabel(self)
        self.tool_data_label.setGeometry(0, 0, self.width, 200)
        self.tool_data_label.setAlignment(Qt.AlignTop)
        self.tool_data_label.setStyleSheet("QLabel { background-color: white; border: 1px solid gray; padding: 10px; }")

        self.tool_treeview = QTreeView(self)
        self.tool_treeview.setGeometry(0, 100, self.width, self.height - 100)
        self.tool_treeview.setHeaderHidden(False)
        self.tool_treeview.setRootIsDecorated(False)
        self.tool_treeview.clicked.connect(self.on_tool_select)
        self.tool_treeview.setSelectionMode(QAbstractItemView.SingleSelection)

        # Create the model for the tree view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Type", "D1", "D2"])
        self.tool_treeview.setModel(self.model)

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

    def display_tool_data(self, tool):
        # Exibe os dados da ferramenta no Label
        tool_data = f"Name: {tool.Name}\nType: {tool.Type}\nD1: {tool.D1}\nD2: {tool.L1}"
        self.tool_data_label.setText(tool_data)

    def add_tool_to_treeview(self, tool):
        item = QStandardItem(tool.Name)
        item.appendRow([QStandardItem(tool.Type), QStandardItem(str(tool.D1)), QStandardItem(str(tool.D2))])
        self.model.appendRow(item)

    def load_tools_from_database(self):
        # Lê as ferramentas do banco de dados
        self.cursor.execute("SELECT * FROM tools")
        tools = self.cursor.fetchall()
        print("Ferramentas lidas do banco de dados: ", len(tools))
        # Adiciona as ferramentas ao Treeview
        for tool_data in tools:
            # Exclua o primeiro elemento (id) dos dados da ferramenta
            tool = Tool(*tool_data[1:])
            self.add_tool_to_treeview(tool)

    def on_tool_select(self, index):
        item = self.model.itemFromIndex(index)
        if item is not None:
            tool_name = item.text()
            # Query the database for the tool with the selected name
            self.cursor.execute("SELECT * FROM tools WHERE name=?", (tool_name,))
            tool_data = self.cursor.fetchone()
            if tool_data is not None:
                tool = Tool(*tool_data[1:])
                self.display_tool_data(tool)

    def closeEvent(self, event):
        # Close the database connection when closing the application
        self.conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool_manager_ui = ToolManagerUI()
    tool_manager_ui.show()
    sys.exit(app.exec_())
