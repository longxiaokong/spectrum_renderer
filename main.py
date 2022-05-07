import sys
from PyQt5 import QtWidgets

from ui import My_Main_window, get_resource_path

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = My_Main_window()
    main_window.show()
    app.exec()
