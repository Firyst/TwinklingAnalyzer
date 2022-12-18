# -*- coding: utf-8 -*-

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog, QTableWidgetItem
from itertools import product
from LogicFunction import LogicFunction, InputException, generate_function_from_table
from string import ascii_letters, digits

VALID_SYMBOLS = ascii_letters + "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" + digits


class InputDialog(QDialog):
    """! Диалоговое окно для ввода логической функции.
    """
    output = None

    def __init__(self):
        """! Инициализация окна
        """
        super().__init__()
        uic.loadUi('resources/InputDialog.ui', self)  # загрузка UI файла
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle("Ввод функции")
        self.buttonCancel.clicked.connect(self.close_dialog)
        self.buttonConfirm.clicked.connect(self.confirm_input)

    def confirm_input(self):
        """! Подтверждение ввода. Вызывается при нажатии на соответствующую кнопку.
        """
        if not self.inputFunction.text():
            self.output = None
            dialog = WarnDialog("Ошибка", "Введите функцию в поле.")
            dialog.exec_()
            return
        try:
            test_func = LogicFunction(self.inputFunction.text())
            self.output = test_func
            self.close()
        except InputException as error:
            self.output = None
            dialog = WarnDialog("Ошибка", error.args[0])
            dialog.exec_()

    def close_dialog(self):
        """! Закрытие диалогового окна и сброс вывода.
        """
        self.output = None  # сбрасываем вывод, чтобы дать сигнал о том, что диалог был закрыт
        self.close()


class ConfirmDialog(QDialog):
    """! Диаолговое окно подтверждения. Имеет две опции - да или нет.
    """
    output = None

    def __init__(self, title: str, text: str):
        """! Инициализация окна
        @param title: название окна
        @param text: текст сообщения
        """
        super().__init__()
        uic.loadUi('resources/ConfirmDialog.ui', self)  # загрузка UI файла
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle(title)
        self.label.setText(text)
        self.buttonCancel.clicked.connect(self.close_dialog)
        self.buttonConfirm.clicked.connect(self.confirm_input)

    def confirm_input(self):
        """! Подтверждение ввода. При вызове сохраняет положительный результат закрывает окно."""
        self.output = True
        self.close()

    def close_dialog(self):
        """! Закрытие диалогового окна и сброс вывода.
        """
        self.output = None  # сбрасываем вывод, чтобы дать сигнал о том, что диалог был закрыт
        self.close()


class TinyInputDialog(QDialog):
    """! Маленькое окошко для ввода названия переменной."""
    output = None

    def __init__(self):
        """! Инициализация окна.
        """
        super().__init__()
        uic.loadUi('resources/InputDialogTiny.ui', self)  # загрузка UI файла
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle("Ввод переменной")
        self.buttonCancel.clicked.connect(self.close_dialog)
        self.buttonConfirm.clicked.connect(self.confirm_input)

    def confirm_input(self):
        """! Подтверждение ввода. Тут же обрабатывает его корректоность.
        """
        if not self.inputLine.text():
            # пусто
            self.output = None
            dialog = WarnDialog("Ошибка", "Введите название")
            dialog.exec_()
            return
        if any(map(lambda i: self.inputLine.text()[i] not in VALID_SYMBOLS, range(len(self.inputLine.text())))):
            # есть некорректные символы!
            dialog = WarnDialog("Ошибка", "Некорректные символы. Можно использовать только символы "
                                          "русского и латинского алфавита. а также цифры 0-9.")
            dialog.exec_()
            return
        if any(map(lambda i: i in self.inputLine.text().lower(), ("not", "or", "xor", "and", "не", "или", "и"))):
            # плохое название (схоже с оператором)
            dialog = WarnDialog("Ошибка", "Название переменной схоже с названием оператора.")
            dialog.exec_()
            return
        if self.inputLine.text()[0] in digits:
            # начинается с цифры
            dialog = WarnDialog("Ошибка", "Название переменной начинается с цифры.")
            dialog.exec_()
            return
        self.output = self.inputLine.text()
        self.close()

    def close_dialog(self):
        """! Закрытие диалогового окна и сброс вывода.
        """
        self.output = None  # сбрасываем вывод, чтобы дать сигнал о том, что диалог был закрыт
        self.close()


class WarnDialog(QDialog):
    """! Предупреждающее/информацинное диалоговое окно.
    """
    def __init__(self, title: str, text: str):
        """! Инициализация окна
        @param title: название окна
        @param text: текст сообщения
        """
        super().__init__()
        uic.loadUi('resources/WarningDialog.ui', self)  # загрузка UI файла
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle(title)
        self.mainLabel.setText(text)
        self.buttonConfirm.clicked.connect(self.close_dialog)

    def close_dialog(self):
        """! Закрытие диалогового окна. Вызывается при нажатии на кнопку.
        """
        self.close()


class TableDialog(QDialog):
    """! Диалоговое окно с вводом таблицы истинности.
    """
    output = None

    def __init__(self):
        """! Инициализация окна
        """
        super().__init__()
        uic.loadUi('resources/TableDialog.ui', self)
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle("Ввод таблицы истинности")

        self.buttonCancel.clicked.connect(self.close_dialog)
        self.buttonConfirm.clicked.connect(self.confirm_input)
        self.varSelector.currentIndexChanged.connect(self.draw_table)
        self.draw_table()

    def draw_table(self):
        """! Отрисовка таблицы. Автоматически считывает значения из выпадающего списка.
        """
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
        """! Подтверждение введенных данных. Проверяет их корректность.
        """
        var_count = self.varSelector.currentIndex() + 2  # количество переменных

        self.output = None  # сбрасываем текущий вывод
        table = []
        values_table = tuple(product((0, 1), repeat=var_count))  # входные значения
        for value_i in range(2 ** var_count):
            try:
                current_value = self.tableWidget.item(value_i, var_count).text()
            except AttributeError:
                # как минимум одно значение не было введено
                self.interrupt_input("Пожалуйста, введите все значения.")
                return
            if str(current_value) in '01':
                table.append((values_table[value_i], int(current_value)))
            else:
                self.interrupt_input("Пожалуйста, введите корректные значения.\nДопустимы только 0 и 1.")
                return

        # получаем функцию в совершенной форме
        self.output = generate_function_from_table(table, self.methodSelector.currentIndex())
        self.close()

    def interrupt_input(self, error_text: str):
        """! Сбрасывает вывод и создает диалоговое окно об ошибке.
        @param error_text: текст ошибки
        """
        self.output = None
        dialog = WarnDialog("Ошибка", error_text)
        dialog.exec_()

    def close_dialog(self):
        """! Закрытие диалогового окна и сброс вывода.
        """
        self.output = None  # сбрасываем вывод, чтобы дать сигнал о том, что диалог был закрыт
        self.close()


class LogicSelectDialog(QDialog):
    """! Диалоговое окно для выбора логических элементов.
    """
    output = None
    output_data = ['not', 'and', 'or', 'xor', 'input']

    def __init__(self):
        """! Инициализация окна.
        """
        super().__init__()
        uic.loadUi('resources/LogicSelectDialog.ui', self)
        self.setWindowFlags(Qt.WindowContextHelpButtonHint ^ self.windowFlags())  # отключить подсказки

        self.setWindowTitle("Выбор элемента")
        self.buttonCancel.clicked.connect(self.close_dialog)
        self.buttonConfirm.clicked.connect(self.confirm_input)
        self.picture.setPixmap(QPixmap("resources/not.png"))

        self.selector.currentIndexChanged.connect(self.change_image)

    def change_image(self):
        """! Смена картинки, когда выбирается другой элемент.
        """
        self.picture.setPixmap(QPixmap('resources/' +
                                       self.output_data[self.selector.currentIndex()] + '.png'))

    def confirm_input(self):
        """! Подтверждение ввода. Output = название логического элемента на английском языке
        """
        self.output = self.output_data[self.selector.currentIndex()]
        self.close()

    def close_dialog(self):
        """! Закрытие диалогового окна и сброс вывода.
        """
        self.output = None  # сбрасываем вывод, чтобы дать сигнал о том, что диалог был закрыт
        self.close()
