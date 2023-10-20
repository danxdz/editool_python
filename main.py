import sys

from PyQt5.QtWidgets import QApplication, QDialog
from tool_manager import ToolManagerUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool_manager_ui = ToolManagerUI()
    tool_manager_ui.show()
    sys.exit(app.exec_())


