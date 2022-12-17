import sys
import os
from typing import List, Tuple
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPixmap, QCursor, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog, QPushButton, QMenu, QFileDialog
from Dialogs import *
from LogicFunction import *
from ImageGenerator import graph
import json
import copy


DEBUG_MODE = 1


def sgn(value):
    """! Функция знака
    @param value: входное значение
    @return: value > 0: 1, value < 0: -1, else 0
    """
    if value == 0:
        return 0
    else:
        return int(value // abs(value))


def load_json(filename) -> dict:
    """! Загрузка JSON-файла сразу в словарь
    @param filename: файл
    @return: dict
    """
    with open(filename) as file:
        return json.load(file)


class SchemeCompilationError(Exception):
    """! Ошибка, вызываемая когда не удается скомпилировать схему.
    """
    pass


class ProgramWindow(QMainWindow):
    """! Главное окно программы
    """
    def __init__(self):
        """! Инициализация окна
        """
        super().__init__()
        uic.loadUi('resources/Window.ui', self)

        self.canvas = MySchemeCanvas(self.schemeTab)
        self.schemeTab.hide()

        self.setWindowIcon(QIcon("resources/not.png"))

        # отключаем меню схемы (оно не нужно по умолчанию)
        self.menuScheme.setEnabled(0)

        # сама функция, с которой работаем
        self.function = None

        # привязка кнопок
        self.buttonTypeManual.clicked.connect(self.create_function_manual)
        self.buttonGenerateFromScheme.clicked.connect(self.open_scheme_editor)
        self.buttonGenerateFromTable.clicked.connect(self.create_function_from_table)

        self.action_scheme_compile.triggered.connect(self.prepare_compilation)  # компиляция схемы
        self.action_scheme_clear.triggered.connect(self.clear_canvas)  # очистка схемы
        self.action_scheme_open.triggered.connect(self.load_scheme)  # загрузка схемы
        self.action_scheme_save.triggered.connect(self.save_scheme)  # сохранение схемы
        self.action_scheme_quit.triggered.connect(self.close_scheme_editor)  # закрытие схемы

        self.button_convert.clicked.connect(self.run_conversion)  # запуск преобразования
        self.conversion_save.clicked.connect(self.save_conversion)  # сохранение преобразования
        self.conversion_clear.clicked.connect(self.clear_conversion_log)  # очистка преобразования

        self.button_analyze_generate.clicked.connect(self.draw_graph)
        self.button_analyze_save.clicked.connect(self.save_graph)


        self.action_about.triggered.connect(self.view_about_page)  # о программе

        self.setup_editor()

    # АНАЛИЗАТОР

    def save_graph(self):
        """! Сохранить график в файл PNG.
        """
        # проверка, есть ли функция
        if self.function is None:
            dialog = WarnDialog("Ошибка", "Функция не задана")
            dialog.exec_()
            return

        # создать диалоговое окно
        dialog = QFileDialog(self)
        dialog.setNameFilter("PNG (*.png)")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            # добавляем расширение, если оно не было указано
            if '.png' not in filename:
                filename += '.png'

            self.draw_graph(filename)

    def draw_graph(self, override_output=''):
        """! Отрисовать график-вейформу функции
        @param override_output: куда сохранить файл. Если не указан, то файл сохранится как temp_graph.png
        """
        if self.function is None:
            dialog = WarnDialog("Ошибка", "Функция не задана")
            dialog.exec_()
            return

        # цвета в соотвествии с выбором в выпадающих списках
        bg_color = ['white', 'black'][self.analayze_color_selector_1.currentIndex()]
        text_color = ['black', 'white'][self.analayze_color_selector_1.currentIndex()]
        graph_color = ['blue', 'red', 'green', 'violet'][self.analayze_color_selector_2.currentIndex()]

        # проверка на сохранение
        if not override_output:
            override_output = "resources/temp_graph.png"
        graph(self.function, text_color, bg_color, graph_color, override_output)

        pixmap = QPixmap(override_output)
        pixmap = pixmap.scaledToHeight(self.graphScrollArea.height() - 24)  # обрезаем по высоте окошка
        self.analyze_graph.setPixmap(pixmap)

    # ПРЕОБРАЗОВАНИЯ

    def run_conversion(self):
        """! Запустить преобразование, заданное
        """
        conv_type = self.conversion_selector.currentIndex()

        if self.function is None:
            # функция не задана
            dialog = WarnDialog("Внимание", 'Сейчас исходная функция не задана.\n'
                                            'Задайте ее на вкладке "запись".')
            dialog.exec_()
            return

        if conv_type <= 4:
            # просто другое отображение
            converted = ("not ", " or ", " and ", " ^ ")  # заменяемые символы
            conversions = (("!", " | ", " & ", " ^ "),
                           ("!", " + ", " * ", " == "),
                           ("¬", " ⋁ ", " ⋀ ", " ⊕ "),
                           ("not ", " or ", " and ", " xor "),
                           ("не ", " или ", " и ", " ^ "))
            exp = self.function.exp
            for r_i in range(len(converted)):
                exp = exp.replace(converted[r_i], conversions[conv_type][r_i])
            self.conversion_log.setPlainText("F = " + exp)
        elif conv_type <= 6:
            # СДНФ/СКНФ
            new_func = generate_function_from_table(self.function.generate_boolean_table(), conv_type % 2)
            self.conversion_log.setPlainText("F = " + new_func.exp.replace('  ', ' '))
        elif conv_type == 7:
            # МКНФ
            try:
                new_func = self.function.simplify_sknf()
                self.conversion_log.setPlainText("F = " + new_func.exp.replace('  ', ' '))
            except Exception:
                dialog = WarnDialog("Ошибка", "Данный метод не способен упростить эту функцию, попробуйте другой.")
                dialog.exec_()
        elif conv_type == 8:
            # МДНФ
            try:
                new_func = self.function.simplify_sdnf()
                self.conversion_log.setPlainText("F = " + new_func.exp.replace('  ', ' '))
            except Exception:
                dialog = WarnDialog("Ошибка", "Данный метод не способен упростить эту функцию, попробуйте другой.")
                dialog.exec_()

    def save_conversion(self):
        """! Сохранить преобразование как текущую функцию
        """
        if self.conversion_log.toPlainText():
            self.function = LogicFunction(self.conversion_log.toPlainText()[4:])
            self.function_text.setText(self.conversion_log.toPlainText())
            self.clear_conversion_log()

    def clear_conversion_log(self):
        """! Очистить вывод преобразований
        """
        self.conversion_log.setPlainText("")

    # UTILITY

    def view_about_page(self):
        """! Открыть окошко "О Программе"
        """
        dialog = WarnDialog("О программе", "Анализатор логических функций TwinklingAnalyzer v1.0 \n\n"
                                           "Баулин Филипп\nСеребрякова Ольга\nМИЭМ НИУ ВШЭ, 2022\n\n"
                                           "https://github.com/Firyst/TwinklingAnalyzer")
        dialog.exec_()

    # ФУНКЦИИ ДЛЯ СХЕМЫ

    def prepare_compilation(self):
        """! Запустить компиляцию и обработать результат
        """
        try:
            func = self.canvas.compile_scheme()  # компиляция
            if func is None:
                return
            dialog = ConfirmDialog(f"Результат компиляции",
                                   f"Компиляция прошла успешно. Полученное выражение:\nF = {func.exp}\n"
                                   f"Сохранить результат?")
            dialog.exec_()
            if dialog.output:
                # сохраняем функцию
                self.function = func
                self.function_text.setText("F = " + func.exp)
                self.close_scheme_editor()
        except SchemeCompilationError as err:
            dialog = WarnDialog("Ошибка компиляции", err.args[0])
            dialog.exec_()

    def clear_canvas(self):
        """! Очистить холст (удалить все виджеты)
        """
        dialog = ConfirmDialog("Подтвердите действие", "Вы действительно хотите удалить все объекты?\n"
                                                       "Это действие необратимо.")
        dialog.exec_()
        if dialog.output == 1:
            self.schemeTab.hide()
            self.canvas.clear_all()

            # добавить стандартный виджет выхода
            obj = self.canvas.new_widget((DraggableWidget(self.schemeTab, 'output', self.canvas)))
            obj.grid_pos = (1, 1)
            self.schemeTab.show()
            self.canvas.render_widgets()

    def canvas_context_menu(self, event):
        """! Обработчик контекстного меню для холста
        @param event: Событие от pyqt
        """
        menu = QMenu(self.schemeTab)
        add_action = menu.addAction("Новый элемент")
        back_action = menu.addAction("Вернуться к началу координат")
        action = menu.exec_(self.schemeTab.mapToGlobal(event.pos()))
        if action == add_action:
            # добавление нового элемента
            dialog = LogicSelectDialog()
            dialog.exec_()
            if dialog.output is not None:
                self.schemeTab.hide()  # для правильной отрисовки нужно отключить события обновления
                try:
                    widget = DraggableWidget(self.schemeTab, dialog.output, self.canvas)
                except InputException:
                    self.schemeTab.show()
                    return
                self.canvas.new_widget(widget)
                widget.grid_pos = ((event.x()) // self.canvas.step + self.canvas.pos[0] // 20,
                                   (event.y()) // self.canvas.step + self.canvas.pos[1] // 20)
                widget.render_object()
                self.schemeTab.show()
                self.canvas.render_widgets()
        elif action == back_action:
            # вернуться к началу координат
            self.canvas.pos = (0, 0)
            self.canvas.render_widgets()

    def close_scheme_editor(self):
        """! Выйти из редактора схем
        """
        self.stackedWidget.setCurrentIndex(0)
        self.menuScheme.setEnabled(0)

    def open_scheme_editor(self):
        """! Открыть редактор схем
        """
        self.stackedWidget.setCurrentIndex(1)
        self.menuScheme.setEnabled(1)
        # self.canvas.new_widget(DraggableWidget(self.schemeTab, 'resources/hecker.jpg', self.canvas))
        self.canvas.render_widgets()

    def setup_editor(self):
        """! Инициализировать окно редактора схем
        """
        self.schemeTab.contextMenuEvent = self.canvas_context_menu

        # добавить стандартный виджет выхода
        obj = self.canvas.new_widget((DraggableWidget(self.schemeTab, 'output', self.canvas)))
        obj.grid_pos = (1, 1)
        self.schemeTab.show()
        self.canvas.render_widgets()

    def save_scheme(self):
        """! Сохранить схему в файл
        """
        # создать диалоговое окно
        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            # добавляем расширение, если оно не было указано
            if '.json' not in filename:
                filename += '.json'
            with open(filename, 'w') as file:
                file.write(json.dumps(self.canvas.save_scheme(), indent=2))

    def load_scheme(self):
        """! Загрузить схему из файла
        """
        # создать диалоговое окно
        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilter("JSON (*.json)")
        if dialog.exec_():
            with open(dialog.selectedFiles()[0], 'r') as file:
                data = json.load(file)
                # проверка валидности JSON
                if data['filetype'] == "TA-scheme-v1":
                    # загружаем схему
                    self.schemeTab.hide()
                    self.canvas.load_scheme(data)
                    self.schemeTab.show()
                    self.canvas.render_widgets()
                else:
                    dialog = WarnDialog("Ошибка", "Не удаётся прочитать файл.\n"
                                                  "Возможно он был поврежден или не является файлом схемы.")
                    dialog.exec_()

    # create methods
    def create_function_manual(self):
        """! Запись функции вручную (строкой)
        """
        dialog = InputDialog()
        dialog.exec_()
        if dialog.output:
            self.function = dialog.output
            self.function_text.setText("F = " + dialog.inputFunction.text())

    def create_function_from_table(self):
        """! Запись функции с помощью таблицы истинности
        """
        dialog = TableDialog()
        dialog.exec_()
        if dialog.output:
            self.function = dialog.output
            self.function_text.setText("F = " + dialog.output.exp)


class DraggableWidget(QLabel):
    """! Перетаскиваем виджет. Используется как логический элемент
    """
    def __init__(self, parent: QWidget, object_type: str, canvas, override_name=''):
        """! Создать виджет объекта схемы
        @param object_type: тип картинки. Возможные значения: and, or, not, inp, out, xor, debug
        """
        super().__init__(parent)
        self.canvas = canvas
        self.connectors: List[Connector] = []
        self.properties = load_json(os.path.join('resources', 'elements', f'{object_type}.json'))

        # переменные для расчета перетаскиваний
        self.cdx, self.cdy = 0, 0  # стартовая позиция курсора
        self.dragging = False  # перетягивается ли объект сейчас
        self.grid_pos = (0, 0)  # позиция на сетке

        self.setScaledContents(True)  # растягивание картинки

        self.obj_type = object_type
        self.setPixmap(QPixmap(self.properties['image']))

        if object_type == 'input':
            # входной сигнал
            if override_name:
                # имя переменной заранее задано, поэтому диалог не нужен
                res = override_name
            else:
                # если просто создаем объект, то вызываем диалог
                dialog = TinyInputDialog()
                dialog.exec_()
                res = dialog.output
                if dialog.output is None:
                    self.deleteLater()
                    raise InputException("Не задано имя переменной")
            # создание подписи
            self.name_widget = QLabel(self)
            self.name_widget.setText(res)
            self.name_widget.setAlignment(Qt.AlignBottom)
            current_font = self.name_widget.font()
            current_font.setPointSize(12)
            self.name_widget.setFont(current_font)
            self.properties['name'] = res
        self.add_connectors()

    def add_connectors(self):
        """! Добавить коннекторы к элементу. Выполняется при инициализации
        """
        for connector in self.properties['connectors']:
            new_connector = Connector(self, self.properties['connectors'][connector], connector)
            self.connectors.append(new_connector)
            self.canvas.connectors.append(new_connector)

    def contextMenuEvent(self, event):
        """! Контекстное меню для элемента.
        @param event: событие от pyqt
        """
        if self.obj_type == "output":
            return  # с выходным сигналом ничего сделать нельзя
        menu = QMenu(self)
        clone_action = menu.addAction("Дублировать")
        delete_action = menu.addAction("Удалить")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == clone_action:
            # дублировать объект
            self.canvas.parent.hide()  # для правильной отрисовки нужно отключить события обновления
            try:
                widget = self.canvas.new_widget(DraggableWidget(self.canvas.parent, self.obj_type, self.canvas))
            except InputException:
                # если дублировали input и не стали задавать имя
                return
            widget.grid_pos = (self.grid_pos[0] + 1, self.grid_pos[1] + 1)  # задать смещенную позицию
            self.canvas.parent.show()
            self.canvas.render_widgets()
        elif action == delete_action:
            # удалить объект
            self.deleteLater()
            for con in self.connectors:
                # удалить все коннекторы
                self.canvas.connectors.remove(con)
                con.deleteLater()
            self.canvas.widgets.remove(self)
            self.canvas.render_widgets()

    def render_object(self):
        """! Отрисовывает объект на схеме.
        """
        self.set_pos(-self.canvas.pos[0] * self.canvas.zoom + self.grid_pos[0] * self.canvas.step,
                     -self.canvas.pos[1] * self.canvas.zoom + self.grid_pos[1] * self.canvas.step)
        self.set_size(self.properties['size'][0] * self.canvas.step,
                      self.properties['size'][1] * self.canvas.step)

    def set_pos(self, x: int, y: int):
        """! Устанавливает положение объекта на экране
        @param x: координата X
        @param y: координата Y
        """
        self.setGeometry(x, y, self.geometry().width(), self.geometry().height())
        self.canvas.compile_connectors()

    def set_size(self, w: int, h: int):
        """! Устанавливает размер объекта
        @param w: ширина
        @param h: высота
        """
        self.setGeometry(self.geometry().x(), self.geometry().y(), w, h)
        self.pixmap().scaled(w, h, Qt.IgnoreAspectRatio)
        for connector in self.connectors:
            connector.render_size()

    def get_grid_pos(self) -> Tuple[int, int]:
        """! Получить координаты объекта на сетке. Метод нужен для унификации с другими объектами.
        @return: Tuple(int, int) - позиция на сетке.
        """
        return self.grid_pos

    def get_size(self) -> Tuple[int, int]:
        """! Получить текущий размер объекта кортежем
        @return:Tuple(int, int) - отрисованный размер объекта.
        """
        return (self.geometry().width(), self.geometry().height())

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        """! Событие нажатия мыши
        @param ev: событие от pyqt
        """
        if ev.button() == Qt.LeftButton:
            # ЛКМ
            self.dragging = 1
            self.cdx, self.cdy = self.x() - QCursor.pos().x(), self.y() - QCursor.pos().y()
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)  # изменить курсор

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        """! Событие отпуска кнопки мыши
        @param ev: событие от pyqt
        """
        self.dragging = 0
        QApplication.restoreOverrideCursor()  # вернуть курсор

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        """! Событие перемещения мыши
        @param ev: событие от pyqt
        """
        if self.dragging:
            # перетаскивание объекта мышкой
            self.grid_pos = ((QCursor.pos().x() + self.cdx + self.canvas.pos[0] * self.canvas.zoom) // self.canvas.step,
                             (QCursor.pos().y() + self.cdy + self.canvas.pos[1] * self.canvas.zoom) // self.canvas.step)
            self.render_object()

    def __repr__(self) -> str:
        """Запись данных объекта в строчку
        @return: строка lObject(data...)
        """
        return f"lObject({self.get_grid_pos()}, {self.obj_type})"


class Connector(QLabel):
    """! Класс пина для соединения элементов
    """

    def __init__(self, parent, offset: tuple, usage: str):
        """! Инициализировать коннектор
        @param parent: родитель, DraggableWidget/Connection
        @param offset: смещение по сетке относительно родителя Tuple(int, int)
        @param usage: тип коннектора input/output/bypass
        """
        self.offset = offset
        super().__init__(parent)
        self.parent = parent
        self.usage = usage

        self.setScaledContents(True)
        self.setPixmap(QPixmap("resources/connector_missing.png"))
        self.test_line = None  # тестовая линия для отрисовки соединений в realtime
        self.render_size()

    def set_type(self, new_type):
        """! Установить тип соединения
        @param new_type: тип (missing, normal, intersection)
        """
        if new_type == "missing":
            self.setPixmap(QPixmap("resources/connector_missing.png"))
        elif new_type == "normal":
            self.setPixmap(QPixmap("resources/connector_default.png"))
        elif new_type == 'intersection':
            self.setPixmap(QPixmap("resources/connector_normal.png"))

    def render_size(self):
        """! Отрисовать коннектор с текущими параметрами
        """
        step = self.parent.canvas.step  # grid step

        self.setGeometry(self.offset[0] * step, self.offset[1] * step,
                         step, step)

    def get_grid_pos(self) -> Tuple[int, int]:
        """! Получить координаты объекта на сетке.
        @return: Tuple(int, int) - позиция на сетке.
        """
        return (self.parent.get_grid_pos()[0] + self.offset[0], self.parent.get_grid_pos()[1] + self.offset[1])

    def set_size(self, w: int, h: int):
        """! Устанавливает размер объекта
        @param w: ширина
        @param h: высота
        """
        self.setGeometry(self.geometry().x(), self.geometry().y(), w, h)
        self.pixmap().scaled(w, h, Qt.KeepAspectRatio)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        """! Событие нажатия мыши
        @param ev: событие от pyqt
        """
        QApplication.setOverrideCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        """! Событие отпуска кнопки мыши
        @param ev: событие от pyqt
        """
        QApplication.restoreOverrideCursor()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        """! Событие перемещения мыши
        @param ev: событие от pyqt
        """
        current_grid_pos = (self.parent.get_grid_pos()[0] + self.offset[0],
                            self.parent.get_grid_pos()[1] + self.offset[1])

        canvas_pos = self.parent.canvas.parent.mapFromGlobal(self.mapToGlobal(ev.pos()))  # к-ты на холсте
        mouse_grid_pos = (round((canvas_pos.x() ) / self.parent.canvas.step + self.parent.canvas.pos[0] / 20 - 0.5),
                          round((canvas_pos.y() ) / self.parent.canvas.step + self.parent.canvas.pos[1] / 20 - 0.5))
        if abs(mouse_grid_pos[0] - current_grid_pos[0]) + abs(mouse_grid_pos[1] - current_grid_pos[1]) > 0:
            # Курсор отодвинулся
            self.parent.canvas.parent.hide()
            if self.test_line is not None:
                # удаляем старую пробную линию, если она была
                self.test_line.delete()
            # создаем пробную линию для отрисовки соединения
            self.test_line = Connection2(self.parent.canvas, current_grid_pos, mouse_grid_pos)
            self.parent.canvas.render_widgets()
            self.parent.canvas.parent.show()
        else:
            # курсор не двигался
            if self.test_line is not None:
                self.test_line.delete()
            self.test_line = None

    def __repr__(self):
        """Запись данных объекта в строчку
        @return: строка Connector(data...)
        """
        return f"Connector({self.get_grid_pos()}, {self.usage})"


class Connection(QLabel):
    """! Класс линии для соединения пинов
    """

    def __init__(self, parent, p1: tuple, p2: tuple, orientation=0):
        """! Инициализровать линию и отрисовать ее. Координаты будут обрезаться по первой точке.
        @param p1: первая точка
        @param p2: вторая точка
        @param orientation: ориентация линии: 0=горизонтальная, 1=вертикальная
        """
        super().__init__(parent.parent)
        self.canvas = parent  # холст, на котором находится линия
        self.orientation = orientation
        self.pos = (p1, p2)

        # создать и добавить два коннектора
        self.connector1 = Connector(self, (0, 0), 'bypass')
        self.connector2 = Connector(self, (0, 0), 'bypass')
        self.canvas.connectors.append(self.connector1)
        self.canvas.connectors.append(self.connector2)

        self.line = QLabel(self)  # видимая линия (смещена на половину шага сетки, чтобы быть по центру)
        self.line.setScaledContents(True)

        # выбор картинки в зависимости от ориентации
        if orientation:
            self.line.setPixmap(QPixmap("resources/lineV.png"))
        else:
            self.line.setPixmap(QPixmap("resources/lineH.png"))

        self.render_line()

    def contextMenuEvent(self, event):
        """! Событие контекстного меню для линии
        @param event: событие от pyqt
        """
        menu = QMenu(self)
        delete_action = menu.addAction("Удалить соединение")
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == delete_action:
            # удалить объект
            self.delete()

    def get_grid_pos(self) -> Tuple[int, int]:
        """! Возвращает позицию на сетке начала линии
        @return: Tuple[int, int] начала линии
        """
        return self.pos[0]

    def delete(self):
        """! Удалить объект и ссылки на него в объекте холста. Также удаляет и коннекторы.
        """
        self.canvas.connectors.remove(self.connector1)
        self.canvas.connectors.remove(self.connector2)
        self.connector1.deleteLater()
        self.connector2.deleteLater()
        self.deleteLater()

        # если не была удалена до этого
        try:
            self.canvas.lines.remove(self)
        except ValueError:
            pass
        self.canvas.compile_connectors()

    def render_line(self):
        """! Отрисовать линию на холсте
        """
        if self.orientation == 0 and self.pos[1][0] < self.pos[0][0]:
            self.pos = (self.pos[1], self.pos[0])
        if self.orientation == 1 and self.pos[1][1] < self.pos[0][1]:
            self.pos = (self.pos[1], self.pos[0])

        self.set_pos(-self.canvas.pos[0] * self.canvas.zoom + self.pos[0][0] * self.canvas.step,
                     -self.canvas.pos[1] * self.canvas.zoom + self.pos[0][1] * self.canvas.step)

        if self.orientation:
            # вертикальная линия
            self.set_size(self.canvas.step, self.canvas.step * (self.pos[1][1] - self.pos[0][1] + 1))
            self.connector2.offset = (0, self.pos[1][1] - self.pos[0][1])

            self.line.setGeometry(int(0.5 * (1 - self.orientation) * self.canvas.step),
                                  int(0.5 * self.orientation * self.canvas.step),
                                  self.canvas.step, self.canvas.step * (self.pos[1][1] - self.pos[0][1]))

        else:
            # горизональная линия
            self.set_size(self.canvas.step * (self.pos[1][0] - self.pos[0][0] + 1), self.canvas.step)
            self.connector2.offset = (self.pos[1][0] - self.pos[0][0], 0)

            self.line.setGeometry(int(0.5 * (1 - self.orientation) * self.canvas.step),
                                  int(0.5 * self.orientation * self.canvas.step),
                                  self.canvas.step * (self.pos[1][0] - self.pos[0][0]), self.canvas.step)

        self.connector1.render_size()
        self.connector2.render_size()

    def set_pos(self, x: int, y: int):
        """! Устанавливает положение левой/верхней точки на экране
        @param x: координата X
        @param y: координата Y
        """
        self.setGeometry(x, y, self.geometry().width(), self.geometry().height())

    def set_size(self, w: int, h: int):
        """! Устанавливает размер соединения (в шагах сетки)
        @param w: ширина
        @param h: высота
        """
        self.setGeometry(self.geometry().x(), self.geometry().y(), w, h)
        self.line.pixmap().scaled(self.line.geometry().width(), self.line.geometry().height(), Qt.IgnoreAspectRatio)

    def __repr__(self):
        """Запись данных объекта в строчку
        @return: строка Line(data...)
        """
        return f"Line{self.pos}"


class Connection2:
    """! Класс, опсиывающий двойную линию (вертикальная + горизонтальная), которой можно соеденить две
    любый точке на холсте
    """
    def __init__(self, parent, p1, p2):
        """! Инициализровать двойное соединение
        @param parent: родитель (холст)
        @param p1: Первая точка
        @param p2: Вторая точка
        """
        self.parent = parent
        self.p1 = p1
        self.p2 = p2
        # создать объектьы линий
        self.line_h = Connection(parent, (p1[0], p2[1]), (p2[0], p2[1]), 0)
        self.line_v = Connection(parent, (p1[0], p1[1]), (p1[0], p2[1]), 1)
        # добавить их в список в родителе-холсте
        self.parent.new_line(self.line_v)
        self.parent.new_line(self.line_h)
        self.set_pos(self.p1, self.p2)

    def delete(self):
        """! Удалить объект и его детей
        """
        try:
            self.line_v.delete()
        except AttributeError:
            pass
        except ValueError:
            pass
        try:
            self.line_h.delete()
        except AttributeError:
            pass
        except ValueError:
            pass

    def render_connection(self):
        """! Отрисовать оба соединения
        """
        if self.line_v is not None:
            self.line_v.render_line()
        if self.line_h is not None:
            self.line_h.render_line()

    def set_pos(self, p1: Tuple[int, int], p2: Tuple[int, int]):
        """! Установить начальную и конечную точки.
        @param p1: первая точка
        @param p2: вторая точка
        """
        self.p1 = p1
        self.p2 = p2
        self.line_h.pos = ((p1[0], p2[1]), (p2[0], p2[1]))
        self.line_v.pos = ((p1[0], p1[1]), (p1[0], p2[1]))
        if (p1[0], p2[1]) == (p2[0], p2[1]):
            self.line_h.delete()
            self.line_h = None
        if (p1[0], p1[1]) == (p1[0], p2[1]):
            self.line_v.delete()
            self.line_v = None
        self.render_connection()


class MySchemeCanvas:
    """! Холст для создания схем
    """
    def __init__(self, parent: QWidget):
        """! Инициализировать холст
        @param parent: родитель - виджет, на который будут добавляться объекты
        """
        self.parent: QWidget = parent
        self.widgets: List[DraggableWidget] = list()
        self.lines: List[Connection] = list()
        self.connectors: List[Connector] = list()

        self.zoom = 1  # к-т приближения
        self.step = self.zoom * 20  # шаг сетки
        self.pos = (0, 0)  # позиция камеры (то есть левого верхнего угла холста)

        # переменные для расчета перетаскиваний
        self.cdx, self.cdy = 0, 0  # стартовая позиция курсора
        self.dragging = False  # перетягивается ли объект сейчас

        # перенаправление событий из виджета
        self.parent.mousePressEvent = self.mouse_press
        self.parent.mouseReleaseEvent = self.mouse_release
        self.parent.mouseMoveEvent = self.mouse_move
        self.parent.wheelEvent = self.scroll

        self.render_widgets()

    def clear_all(self):
        """! Удалить все объекты на поле"""
        for con in self.connectors:
            con.parent.deleteLater()
            con.deleteLater()
        self.widgets = []
        self.lines = []
        self.connectors = []

    def save_scheme(self) -> dict:
        """! Преобразовать схему в JSON-словарь
        @return: dict со всеми элементами
        """

        # установим специальную метку, чтобы определять что файл валидный
        output_data = {'filetype': 'TA-scheme-v1', 'objects': []}

        added = set()  # учет всех добавленных
        for con in self.connectors:
            if con.parent not in added:
                # проверяем родителя коннектора
                obj = {}
                if type(con.parent) == DraggableWidget:
                    # логический элемент
                    obj['type'] = 'Element'
                    obj['obj_type'] = con.parent.obj_type
                    obj['pos'] = list(con.parent.get_grid_pos())
                    if 'name' in con.parent.properties:
                        obj['name'] = con.parent.properties['name']
                elif type(con.parent) == Connection:
                    # линия
                    obj['type'] = 'Line'
                    obj['pos1'] = con.parent.pos[0]
                    obj['pos2'] = con.parent.pos[1]
                    obj['orientation'] = con.parent.orientation
                if obj:
                    output_data['objects'].append(obj)
                    added.add(con.parent)
            if con not in added:
                # проверяем сам коннектор
                # а зачем..
                pass
        return output_data

    def load_scheme(self, objects: dict):
        """! Загружает схему из JSON-словаря
        @param objects: результат json.load()
        """
        self.clear_all()
        for obj in objects['objects']:
            if obj['type'] == 'Element':
                if 'name' in obj:
                    # это input (у него есть особенный параметр - имя)
                    new = self.new_widget(DraggableWidget(self.parent, obj['obj_type'], self, obj['name']))
                else:
                    # это всё остальное
                    new = self.new_widget(DraggableWidget(self.parent, obj['obj_type'], self))
                new.grid_pos = tuple(obj['pos'])
            elif obj['type'] == 'Line':
                self.new_line(Connection(self, tuple(obj['pos1']), tuple(obj['pos2']), obj['orientation']))

    def new_widget(self, widget: DraggableWidget):
        """ ! Добавить виджет на холст
        @param widget: Виджет класса DraggableWidget
        """
        self.widgets.append(widget)
        return widget

    def new_line(self, widget: Connection):
        """ ! Добавить виджет на холст
        @param widget: Виджет класса Connection
        """
        self.lines.append(widget)
        return widget

    def render_widgets(self):
        """! Отрисовывает все виджеты
        """
        for widget in self.widgets:
            widget.render_object()

        for line in self.lines:
            line.render_line()

    def compile_connectors(self):
        """! Провести расчет всех соединений (коннектор) на холсте
        @return сгрупированные по позиции коннекторы
        """
        # будем группировать по позиции на холсте
        grouped = dict()
        for connector in self.connectors:
            pos = connector.get_grid_pos()
            if pos not in grouped:
                grouped[pos] = [connector]
            else:
                grouped[pos].append(connector)

        for pos in grouped:
            if len(grouped[pos]) > 1:
                for connector in grouped[pos]:
                    if len(grouped[pos]) > 2:
                        connector.set_type("intersection")
                    else:
                        connector.set_type("normal")
            elif len(grouped[pos]) == 1:
                grouped[pos][0].set_type("missing")

        return grouped

    def compile_scheme(self):
        """! Преобразует схему в выражение
        @return: LogicFunction от схемы
        """
        def debug_print(a):
            # мини-функция для отладки
            if DEBUG_MODE:
                print(a)

        def get_source(cur_w, vis=None):
            """! Ищет первый подключенный выход к сети соединений
            @param cur_w: начальный объект
            @param vis: список посещенных
            @return: найденный коннектор
            """
            if vis is None:
                vis = list()
            vis.append(cur_w)
            if type(cur_w) == Connector:
                if cur_w.usage == 'out':
                    return cur_w
                elif cur_w.usage == 'bypass':
                    # проходной коннектор
                    connected = grouped[cur_w.get_grid_pos()].copy()
                    for con in connected:
                        if con not in vis:
                            # смотрим, есть ли искомый коннектор в данной ветке
                            if con.usage == 'out':
                                return cur_w
                            if con.usage[2:] == 'in':
                                return
                            vis.append(con)
                            res = get_source(con.parent, vis.copy())
                            if res is not None:
                                debug_print(f"Обходчик ветвей нашел {res}")
                                # если что-то нашлось, возвращаем
                                return res
            elif type(cur_w) == Connection:
                # у линии может быть всего 2 конектора, поэтому просто проверяем каждый из них
                if cur_w.connector1 not in vis:
                    return get_source(cur_w.connector1, vis.copy())
                if cur_w.connector2 not in vis:
                    return get_source(cur_w.connector2, vis.copy())

        def rec(cur_w, vis):
            """ ! Рекурсионный обход схемы
            @param vis: Посещенные объекты
            @param cur_w: текущий виджет
            @return: выражение
            """
            if vis is None:
                vis = set()
            debug_print(f"Обработка: {cur_w}")
            if cur_w in vis:
                # уже были
                return ''
            vis.add(cur_w)
            if type(cur_w) == DraggableWidget:
                # обработка объекта
                debug_print(f"Обработан элемент {cur_w.obj_type} на позиции {cur_w.get_grid_pos()}")

                def get_con(con_name):
                    """! Возвращает коннектор объекта с заданным именем.
                    @param con_name: название
                    @return: Connector
                    """
                    for con in cur_w.connectors:
                        if con.usage == con_name:
                            return con

                if cur_w.obj_type == "input":
                    # для инпута возвращаем название переменной
                    return cur_w.properties['name']
                elif cur_w.obj_type == "not":
                    # NOT
                    return f"not {rec(get_con('in1'), vis.copy())}"
                elif cur_w.obj_type == 'output':
                    # выход
                    return rec(get_con("in"), vis.copy())
                else:
                    # бинарный опреатор - возвращаем сам оператор и операнды
                    return f"({rec(get_con('in1'), vis.copy())} {cur_w.properties['operator']} " \
                           f"{rec(get_con('in2'), vis.copy())})"
            elif type(cur_w) == Connector:
                # обрабатываем коннектор
                if cur_w.usage == "out":
                    # для выходного коннектора просто запускаем обход по родителю
                    return rec(cur_w.parent, vis.copy())
                elif cur_w.usage[:2] == "in":
                    # входной коннектор - для него смотрим подключенные
                    connected = grouped[cur_w.get_grid_pos()].copy()
                    if len(connected) == 1:
                        raise SchemeCompilationError("Имеется неподключенный вход на элементе")
                    elif (len(connected)) > 2:
                        raise SchemeCompilationError("Ко входу подключено несколько выходов.")
                    else:
                        # всё хорошо
                        debug_print(f"Обработан коннектор на позиции {cur_w.get_grid_pos()}\n"
                                    f"Подключенные: {connected}")
                        connected.remove(cur_w)
                        return rec(connected[0], vis.copy())
                elif cur_w.usage == "bypass":
                    # обычный коннектор, соединяющий прямые
                    connected = grouped[cur_w.get_grid_pos()].copy()
                    debug_print(f"Подключенные: {connected}")
                    if len(connected) <= 2:
                        # просто линейный коннектор
                        for itsc_con in connected:
                            if itsc_con.parent not in vis:  # ищем непосещенную линию
                                vis.add(itsc_con)
                                return rec(itsc_con.parent, vis.copy())  # обрабатываем линию
                    else:
                        # пересечение, запускаем поиск выхода
                        return rec(get_source(cur_w), vis.copy())

            elif type(cur_w) == Connection:
                # у линии может быть всего 2 конектора, поэтому просто проверяем каждый из них
                debug_print(f"Обработка линии")
                if cur_w.connector1 not in vis:
                    return rec(cur_w.connector1, vis.copy())
                if cur_w.connector2 not in vis:
                    return rec(cur_w.connector2, vis.copy())

        debug_print("-= Начало компиляции =-")

        self.render_widgets()
        grouped = self.compile_connectors()
        debug_print(f"Коннекторы скомпилированы успешно, всего {len(grouped)} точек")

        output_node = None
        # поиск выходного элемента, с которого начнем обход
        for widget in self.widgets:
            if widget.obj_type == "output":
                output_node = widget
                break
        debug_print("Найден выходной коннектор")

        try:
            # пробуем скомпилировать
            # функция также может вызывать исключения SchemeCompilationError,
            # они обрабатываются в prepare_compilation
            result = rec(output_node, None)
            return LogicFunction(result)
        except InputException as error:
            # схема скомпилировалсь, но функция неправильная
            dialog = WarnDialog("Ошибка компиляции", error.args[0] + f"\nРаспознанное выражение: {result}")
            dialog.exec_()

    def set_zoom(self, zoom: int):
        """! Устанавливает приближение на холсте
        @param zoom: множитель приближения
        """
        w, h = self.parent.size().width(), self.parent.size().height()
        if zoom > self.zoom:
            self.pos = (int(self.pos[0] + 0.5 * (w - w * (self.zoom / zoom))),
                        int(self.pos[1] + 0.5 * (h - h * (self.zoom / zoom))))
        else:
            self.pos = (int(self.pos[0] + 0.5 * (w * (zoom / self.zoom) - w)),
                        int(self.pos[1] + 0.5 * (h * (zoom / self.zoom) - h)))
        self.zoom = zoom
        self.step = zoom * 20
        self.render_widgets()

    def move_field(self, mx: int, my: int):
        """ ! Подвинуть "камеру" на поле
        @param mx: смещение по X
        @param my: смещение по Y
        """
        self.pos = (self.pos[0] + mx, self.pos[1] + my)
        self.render_widgets()

    def scroll(self, event: QtGui.QWheelEvent):
        """! Событие прокрутки колесиком мыши
        @param event: событие от pyqt
        """
        scr_x, scr_y = event.angleDelta().x(), event.angleDelta().y()
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:  # нажат CTRL
            if scr_y > 0:
                # приближение
                self.set_zoom(min(2, self.zoom + 1))
            elif scr_y < 0:
                # отдаление
                self.set_zoom(max(self.zoom - 1, 1))
            return
        elif modifiers == Qt.ShiftModifier:  # нажат SHIFT
            # горизонтальный скролл
            scr_x, scr_y = scr_y, scr_x
        self.move_field(scr_x // -24, scr_y // -24)

    def mouse_press(self, ev: QtGui.QMouseEvent) -> None:
        """Нажатие скм
        @param ev: событие от pyqt
        """
        if ev.button() == Qt.MidButton:
            self.dragging = 1
            self.cdx, self.cdy = QCursor.pos().x(), QCursor.pos().y()
            QApplication.setOverrideCursor(Qt.SizeAllCursor)

    def mouse_release(self, ev: QtGui.QMouseEvent) -> None:
        """Отпуск скм
        @param ev: событие от pyqt
        """
        self.dragging = 0
        QApplication.restoreOverrideCursor()

    def mouse_move(self, ev: QtGui.QMouseEvent) -> None:
        """Движение холста при зажатии СКМ
        @param ev: событие от pyqt
        """
        if self.dragging:
            # перемещение по холсту
            self.pos = (int(self.pos[0] + (self.cdx - QCursor.pos().x())),
                        int(self.pos[1] + (self.cdy - QCursor.pos().y())))
            self.cdx, self.cdy = QCursor.pos().x(), QCursor.pos().y()
            self.render_widgets()
