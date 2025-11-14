# main.py
from gui import IPCDebuggerGUI
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = IPCDebuggerGUI()
    win.show()
    sys.exit(app.exec_())
