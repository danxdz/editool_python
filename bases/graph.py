import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
import pyqtgraph.opengl as gl
import numpy as np

class ToolManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Criar um widget 3D
        self.plot_widget = gl.GLViewWidget()

        # Configurar a cena 3D
        self.plot_widget.pan(0, 0, 0)
        self.plot_widget.setCameraPosition(distance=10)

        # Adicionar widget à janela principal
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)

        # Adicionar botão para adicionar ferramenta
        add_tool_button = QPushButton("Adicionar Ferramenta")
        add_tool_button.clicked.connect(self.add_tool)
        layout.addWidget(add_tool_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def add_tool(self):
        # Exemplo: Adicionar uma fresa
        meshdata = gl.MeshData.cylinder(rows=10, cols=20, radius=[0.5, 0.3, 0.2], length=[1, 0.8, 0.6])
        item = gl.GLMeshItem(meshdata=meshdata, smooth=True, shader="balloon")
        self.plot_widget.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToolManagerWindow()
    window.show()
    sys.exit(app.exec_())
