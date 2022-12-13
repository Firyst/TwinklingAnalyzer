import sys
import os
from typing import List, Tuple
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog, QPushButton, QMenu, QLineEdit
from Dialogs import *
import json


def sgn(value):
    """
    Функция знака
    @param value: входное значение
    @return: value > 0: 1, value < 0: -1, else 0
    """
    if value == 0:
        return 0
    else:
        return int(value // abs(value))


def load_json(filename):
    with open(filename) as file:
        return json.load(file)


class ProgramWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('resources/Window.ui', self)

        # привязка кнопок
        self.buttonTypeManual.clicked.connect(self.createFunctionManual)
        self.buttonGenerateFromScheme.clicked.connect(self.createFunctionFromScheme)
        self.buttonGenerateFromTable.clicked.connect(self.createFunctionFromTable)

        self.canvas = MySchemeCanvas(self.schemeTab)
        # self.canvas.new_widget(DraggableWidget(self.schemeTab, 'resources/hecker.jpg', self.canvas))
        self.canvas.render_widgets()
        self.schemeTab.contextMenuEvent = self.canvas_context_menu

        # test_line = self.canvas.new_line(Connection(self.canvas, (0, 1), (5, 1), 0))
        # test_line = self.canvas.new_line(Connection(self.canvas, (0, 0), (0, 5), 1))
        # test_line = self.canvas.new_line(Connection(self.canvas, (1, 1), (1, 3), 1))

        # test_con = Connection2(self.canvas, (0, 0), (3, -3))

        self.canvas.new_widget((DraggableWidget(self.schemeTab, 'output', self.canvas)))
        self.canvas.render_widgets()

    def canvas_context_menu(self, event):
        print(event.x(), event.y())
        menu = QMenu(self.schemeTab)
        add_action = menu.addAction("Новый элемент")
        back_action = menu.addAction("Вернуться к началу координат")
        action = menu.exec_(self.schemeTab.mapToGlobal(event.pos()))
        if action == add_action:
            dialog = LogicSelectDialog()
            dialog.exec_()
            if dialog.output is not None:
                self.schemeTab.hide()  # для правильной отрисовки нужно отключить события обновления
                widget = self.canvas.new_widget(DraggableWidget(self.schemeTab, dialog.output, self.canvas))
                widget.grid_pos = ((self.canvas.pos[0] + event.x()) // self.canvas.step,
                                   (self.canvas.pos[1] + event.y()) // self.canvas.step)
                widget.render_object()
                self.schemeTab.show()
                print(len(self.canvas.widgets))
                self.canvas.render_widgets()
        elif action == back_action:
            self.canvas.pos = (0, 0)
            self.canvas.render_widgets()

    def create_canvas_layout(self):
        pass

    def canvas_mouse_event(self, ev):
        print(ev.x(), ev.y())

    # create methods
    def createFunctionManual(self):
        self.canvas.new_widget(DraggableWidget(self.schemeTab, 'resources/hecker.jpg', self.canvas))
        dialog = InputDialog()
        dialog.exec_()

    def createFunctionFromScheme(self):
        dialog = WarnDialog("Ошибка", "Рисунок некорректный")
        dialog.exec_()

    def createFunctionFromTable(self):
        dialog = TableDialog()
        dialog.exec_()


class DraggableWidget(QLabel):
    def __init__(self, parent: QWidget, object_type: str, canvas):
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
        self.grid_pos = (0, 0)

        self.setScaledContents(True)

        self.image = object_type
        self.setPixmap(QPixmap(self.properties['image']))

        self.add_connectors()

        if object_type == 'input':
            self.name_widget = QLineEdit(self)
            self.name_widget.setFocusPolicy(Qt.StrongFocus)
            self.name_widget.focus = False
            self.name_widget.returnPressed.connect(self.defocus)

    def defocus(self):
        print(111)
        self.name_widget.hide()
        self.name_widget.focus = False
        self.name_widget.deselect()
        self.name_widget.show()

    def add_connectors(self):
        for connector in self.properties['connectors']:
            new_connector = Connector(self, self.properties['connectors'][connector])
            self.connectors.append(new_connector)
            self.canvas.connectors.append(new_connector)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        clone_action = menu.addAction("Дублировать")
        delete_action = menu.addAction("Удалить")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == clone_action:
            # дублировать объект
            self.canvas.parent.hide()  # для правильной отрисовки нужно отключить события обновления
            widget = self.canvas.new_widget(DraggableWidget(self.canvas.parent, self.image, self.canvas))
            widget.grid_pos = (self.grid_pos[0] + 1, self.grid_pos[1] + 1)
            self.canvas.parent.show()
            self.canvas.render_widgets()
        elif action == delete_action:
            # удалить объект
            self.deleteLater()
            for con in self.connectors:
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

    def get_grid_pos(self):
        """! Получить координаты объекта на сетке.
        """
        return self.grid_pos

    def get_size(self) -> tuple:
        """! Возвращает текущий размер объекта кортежем
        @return:
        """
        return (self.geometry().width(), self.geometry().height())

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self.dragging = 1
            self.cdx, self.cdy = self.x() - QCursor.pos().x(), self.y() - QCursor.pos().y()
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.dragging = 0
        QApplication.restoreOverrideCursor()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.dragging:
            # перетаскивание объекта мышкой
            self.grid_pos = ((QCursor.pos().x() + self.cdx + self.canvas.pos[0] * self.canvas.zoom) // self.canvas.step,
                             (QCursor.pos().y() + self.cdy + self.canvas.pos[1] * self.canvas.zoom) // self.canvas.step)
            self.render_object()


class Connector(QLabel):
    """! Класс пина для соединения элементов
    """

    def __init__(self, parent, offset: tuple):
        self.offset = offset
        print(offset)
        super().__init__(parent)
        self.parent = parent
        self.setScaledContents(True)
        self.setPixmap(QPixmap("resources/connector_missing.png"))
        self.test_line = None
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
        # self.set_size(, self.parent.canvas.step)
        step = self.parent.canvas.step  # grid step

        self.setGeometry(self.offset[0] * step, self.offset[1] * step,
                         step, step)

    def get_grid_pos(self):
        return (self.parent.get_grid_pos()[0] + self.offset[0], self.parent.get_grid_pos()[1] + self.offset[1])

    def set_size(self, w: int, h: int):
        """! Устанавливает размер объекта
        @param w: ширина
        @param h: высота
        """
        self.setGeometry(self.geometry().x(), self.geometry().y(), w, h)
        self.pixmap().scaled(w, h, Qt.KeepAspectRatio)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        QApplication.setOverrideCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        QApplication.restoreOverrideCursor()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.underMouse():
            current_grid_pos = ((self.geometry().x() + self.parent.geometry().x() + self.parent.canvas.pos[0])
                                // self.parent.canvas.step,
                                (self.geometry().y() + self.parent.geometry().y() + self.parent.canvas.pos[1])
                                // self.parent.canvas.step)

            canvas_pos = self.parent.canvas.parent.mapFromGlobal(self.mapToGlobal(ev.pos()))  # к-т на холсте
            mouse_grid_pos = ((canvas_pos.x() + self.parent.canvas.pos[0]) // self.parent.canvas.step,
                              (canvas_pos.y() + self.parent.canvas.pos[1]) // self.parent.canvas.step)

            if abs(mouse_grid_pos[0] - current_grid_pos[0]) + abs(mouse_grid_pos[1] - current_grid_pos[1]) > 0:
                # Курсор отодвинулся
                self.parent.canvas.parent.hide()
                if self.test_line is not None:
                    self.test_line.delete()
                self.test_line = Connection2(self.parent.canvas, current_grid_pos, mouse_grid_pos)
                self.parent.canvas.render_widgets()
                self.parent.canvas.parent.show()
            else:
                if self.test_line is not None:
                    self.test_line.delete()
                self.test_line = None


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
        self.connector1 = Connector(self, (0, 0))
        self.connector2 = Connector(self, (0, 0))
        self.canvas.connectors.append(self.connector1)
        self.canvas.connectors.append(self.connector2)


        self.line = QLabel(self)  # видимая линия (смещена на половину шага сетки, чтобы быть по центру)
        self.line.setScaledContents(True)
        self.disabled = False  # отключено ли соединение

        if orientation:
            self.line.setPixmap(QPixmap("resources/lineV.png"))
        else:
            self.line.setPixmap(QPixmap("resources/lineH.png"))

        self.render_line()

    def disable(self):
        if self.disabled:
            return
        self.disabled = True
        self.hide()
        self.connector1.hide()
        self.connector2.hide()
        self.canvas.connectors.remove(self.connector1)
        self.canvas.connectors.remove(self.connector2)

    def enable(self):
        if not self.disabled:
            return
        self.disabled = False
        self.show()
        self.connector1.show()
        self.connector2.show()
        self.canvas.connectors.append(self.connector1)
        self.canvas.connectors.append(self.connector2)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        delete_action = menu.addAction("Удалить соединение")
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == delete_action:
            # удалить объект
            self.delete()

    def get_grid_pos(self):
        """! Возвращает позицию на сеткеначала линии
        """
        return self.pos[0]

    def delete(self):
        self.canvas.connectors.remove(self.connector1)
        self.canvas.connectors.remove(self.connector2)
        self.connector1.deleteLater()
        self.connector2.deleteLater()
        self.deleteLater()

        try:
            self.canvas.lines.remove(self)
        except ValueError:
            pass
        self.canvas.compile_connectors()

    def render_line(self):
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


class Connection2:
    """! Класс, опсиывающий двойную линию (вертикальная + горизонтальная), которой можно соеденить две
    любый точке на холсте
    """
    def __init__(self, parent, p1, p2):
        self.parent = parent
        self.p1 = p1
        self.p2 = p2
        self.line_h = Connection(parent, (p1[0], p2[1]), (p2[0], p2[1]), 0)
        self.line_v = Connection(parent, (p1[0], p1[1]), (p1[0], p2[1]), 1)
        self.parent.new_line(self.line_v)
        self.parent.new_line(self.line_h)
        self.set_pos(self.p1, self.p2)

    def delete(self):
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
        if self.line_v is not None:
            self.line_v.render_line()
        if self.line_h is not None:
            self.line_h.render_line()

    def set_pos(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.line_h.pos = ((p1[0], p2[1]), (p2[0], p2[1]))
        self.line_v.pos = ((p1[0], p1[1]), (p1[0], p2[1]))
        print((p1[0], p2[1]), (p2[0], p2[1]), (p1[0], p1[1]), (p1[0], p2[1]))
        if (p1[0], p2[1]) == (p2[0], p2[1]):
            self.line_h.delete()
            self.line_h = None
        if (p1[0], p1[1]) == (p1[0], p2[1]):
            self.line_v.delete()
            self.line_v = None
        self.render_connection()


class MySchemeCanvas:
    def __init__(self, parent: QWidget):
        self.parent: QWidget = parent
        self.widgets: List[DraggableWidget] = list()  # all widget on canvas
        self.lines: List[Connection] = list()  # all lines on canvas
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

        self.compile_connectors()

    def compile_connectors(self):
        """! Провести расчет всех соединений (коннектор) на холсте
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

    def set_zoom(self, zoom: int):
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
        scr_x, scr_y = event.angleDelta().x(), event.angleDelta().y()
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            # приближение
            if scr_y > 0:
                self.set_zoom(min(2, self.zoom + 1))
            elif scr_y < 0:
                self.set_zoom(max(self.zoom - 1, 1))
            return
        elif modifiers == Qt.ShiftModifier:
            # горизонтальный скролл
            scr_x, scr_y = scr_y, scr_x
        self.move_field(scr_x // -24, scr_y // -24)

    def mouse_press(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.MidButton:
            self.dragging = 1
            self.cdx, self.cdy = QCursor.pos().x(), QCursor.pos().y()
            QApplication.setOverrideCursor(Qt.SizeAllCursor)

    def mouse_release(self, ev: QtGui.QMouseEvent) -> None:
        self.dragging = 0
        QApplication.restoreOverrideCursor()

    def mouse_move(self, ev: QtGui.QMouseEvent) -> None:
        if self.dragging:
            # перемещение по холсту
            self.pos = (int(self.pos[0] + (self.cdx - QCursor.pos().x())),
                        int(self.pos[1] + (self.cdy - QCursor.pos().y())))
            self.cdx, self.cdy = QCursor.pos().x(), QCursor.pos().y()
            self.render_widgets()
