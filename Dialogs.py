from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog, QTableWidgetItem
from itertools import product
from LogicFunction import LogicFunction, InputException


class InputDialog(QDialog):
    output = None

    def __init__(self):
        super().__init__()
        uic.loadUi('resources/InputDialog.ui', self)
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle("Ввод функции")
        self.buttonCancel.clicked.connect(self.close_dialog)
        self.buttonConfirm.clicked.connect(self.confirm_input)

    def confirm_input(self):
        if not self.inputFunction.text():
            self.output = None
            dialog = WarnDialog("Ошибка", "Введите функцию в поле.")
            dialog.exec_()
            return
        try:
            test_func = LogicFunction(self.inputFunction.text())
            self.output = test_func
        except InputException as error:
            self.output = None
            dialog = WarnDialog("Ошибка", error.args[0])
            dialog.exec_()

    def close_dialog(self):
        self.output = None  # сбрасываем вывод, чтобы дать сигнал о том, что диалог был закрыт
        self.close()


class WarnDialog(QDialog):
    def __init__(self, title, text):
        super().__init__()
        uic.loadUi('resources/WarningDialog.ui', self)
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle(title)
        self.mainLabel.setText(text)
        self.buttonConfirm.clicked.connect(self.close_dialog)

    def confirm_input(self):
        pass

    def close_dialog(self):
        self.close()


class TableDialog(QDialog):
    output = []

    def __init__(self):
        super().__init__()
        uic.loadUi('resources/TableDialog.ui', self)
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle("Ввод таблицы истинности")

        self.buttonCancel.clicked.connect(self.close_dialog)
        self.buttonConfirm.clicked.connect(self.confirm_input)
        self.varSelector.currentIndexChanged.connect(self.draw_table)
        self.draw_table()

    def draw_table(self):
        # сначала очищаем таблицу
        while self.tableWidget.rowCount():
            self.tableWidget.removeRow(0)

        var_count = self.varSelector.currentIndex() + 2  # количество переменных

        # задаем количество строк и столбцов
        self.tableWidget.setColumnCount(var_count + 1)
        self.tableWidget.setRowCount(2 ** var_count)

        # задаем красивые название столбцов
        for i, label in enumerate(['a', 'b', 'c', 'd', 'e', 'f'][:var_count] + ['Знач']):
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(label))

        # заполняем таблицу значениями
        for iy, string in enumerate(product((0, 1), repeat=var_count)):
            for ix, value in enumerate(string):
                new_item = QTableWidgetItem(str(value))  # создаем элемент таблицы со значение
                new_item.setFlags(Qt.ItemIsEditable)  # выключаем возможность редактировать элемент
                self.tableWidget.setItem(iy, ix, new_item)

        # меняем размер по содержимому
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def confirm_input(self):
        var_count = self.varSelector.currentIndex() + 2  # количество переменных

        self.output = []  # сбрасываем текущий вывод
        values_table = tuple(product((0, 1), repeat=var_count))  # входные значения
        for value_i in range(2 ** var_count):
            try:
                current_value = self.tableWidget.item(value_i, var_count).text()
            except AttributeError:
                # как минимум одно значение не было введено
                self.interrupt_input("Пожалуйста, введите все значения.")
                return
            if str(current_value) in '01':
                self.output.append((values_table[value_i], int(current_value)))
            else:
                self.interrupt_input("Пожалуйста, введите корректные значения.\nДопустимы только 0 и 1.")
                return
        print(self.output)

    def interrupt_input(self, error_text):
        self.output = []
        dialog = WarnDialog("Ошибка", error_text)
        dialog.exec_()

    def close_dialog(self):
        self.output = None  # сбрасываем вывод, чтобы дать сигнал о том, что диалог был закрыт
        self.close()


class LogicSelectDialog(QDialog):
    output = None
    images = {0: "resources/not.png", 1: "resources/and.png", 2: "resources/or.png", }

    def __init__(self):
        super().__init__()
        uic.loadUi('resources/LogicSelectDialog.ui', self)
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle("Выбор элемента")
        self.buttonCancel.clicked.connect(self.close_dialog)
        self.buttonConfirm.clicked.connect(self.confirm_input)
        self.picture.setPixmap(QPixmap("resources/not.png"))

        self.selector.currentIndexChanged.connect(self.change_image)

    def change_image(self):
        self.picture.setPixmap(QPixmap(self.images[self.selector.currentIndex()]))

    def confirm_input(self):
        self.output = self.selector.currentIndex()
        self.close()

    def close_dialog(self):
        self.output = None  # сбрасываем вывод, чтобы дать сигнал о том, что диалог был закрыт
        self.close()