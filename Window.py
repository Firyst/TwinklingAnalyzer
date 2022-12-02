import sys
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog
from Dialogs import InputDialog, WarnDialog, TableDialog


class ProgramWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('resources/Window.ui', self)

        # привязка кнопок
        self.buttonTypeManual.clicked.connect(self.createFunctionManual)
        self.buttonGenerateFromScheme.clicked.connect(self.createFunctionFromScheme)
        self.buttonGenerateFromTable.clicked.connect(self.createFunctionFromTable)

    # create methods
    def createFunctionManual(self):
        dialog = InputDialog()
        dialog.exec_()

    def createFunctionFromScheme(self):
        dialog = WarnDialog("Ошибка", "Рисунок неккоректный")
        dialog.exec_()

    def createFunctionFromTable(self):
        dialog = TableDialog()
        dialog.exec_()