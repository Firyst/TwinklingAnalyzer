# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication
import sys
from PyQt5 import QtGui
from Window import ProgramWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont("resources/SourceCodePro-Black.ttf")  # load font for other OS
    win = ProgramWindow()
    win.show()
    sys.exit(app.exec_())
