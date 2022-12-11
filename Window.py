import sys
from typing import List
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog, QPushButton, QMenu
from Dialogs import *


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


class ProgramWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('resources/Window.ui', self)

        # привязка кнопок
        self.buttonTypeManual.clicked.connect(self.createFunctionManual)
        self.buttonGenerateFromScheme.clicked.connect(self.createFunctionFromScheme)
        self.buttonGenerateFromTable.clicked.connect(self.createFunctionFromTable)

        self.canvas = MySchemeCanvas(self.schemeTab)
        # self.schemeTab.mouseMoveEvent = self.canvas.mouse_move
        # self.canvas.new_widget(DraggableWidget(self.schemeTab, 'debug', self.canvas))
        self.canvas.new_widget(DraggableWidget(self.schemeTab, 'resources/hecker.jpg', self.canvas))
        self.canvas.render_widgets()
        self.schemeTab.contextMenuEvent = self.canvas_context_menu

    def canvas_context_menu(self, event):
        menu = QMenu(self.schemeTab)
        add_action = menu.addAction("Новый элемент")
        action = menu.exec_(self.schemeTab.mapToGlobal(event.pos()))
        if action == add_action:
            dialog = LogicSelectDialog()
            dialog.exec_()
            if dialog.output is not None:
                self.schemeTab.hide()  # для правильной отрисовки нужно отключить события обновления
                self.canvas.new_widget(DraggableWidget(self.schemeTab, dialog.images[dialog.output], self.canvas))
                self.schemeTab.show()
                print(len(self.canvas.widgets))
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

        # переменные для расчета перетаскиваний
        self.cdx, self.cdy = 0, 0  # стартовая позиция курсора
        self.dragging = False  # перетягивается ли объект сейчас
        self.grid_pos = (0, 0)

        self.setScaledContents(True)

        self.setPixmap(QPixmap(object_type))

        self.set_size(50, 50)

    def render_object(self):
        """! Отрисовывает объект на схеме.
        """
        self.set_pos(-self.canvas.pos[0] * self.canvas.zoom + self.grid_pos[0] * self.canvas.step,
                     -self.canvas.pos[1] * self.canvas.zoom + self.grid_pos[1] * self.canvas.step)
        self.set_size(50 * self.canvas.zoom, 50 * self.canvas.zoom)

    def set_pos(self, x: int, y: int):
        """! Устанавливает положение объекта на экране
        @param x: координата X
        @param y: координата Y
        """
        self.setGeometry(x, y, self.geometry().width(), self.geometry().height())

    def set_size(self, w: int, h: int):
        """! Устанавливает размер объекта
        @param w: ширина
        @param h: высота
        """
        self.setGeometry(self.geometry().x(), self.geometry().y(), w, h)
        self.pixmap().scaled(w, h, Qt.KeepAspectRatio)

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


class MySchemeCanvas:
    def __init__(self, parent: QWidget):
        self.parent: QWidget = parent
        self.widgets: List[DraggableWidget] = list()  # all widget on canvas
        self.lines = list()  # all lines on canvas
        self.connections = list()

        self.zoom = 1  # к-т приближения
        self.step = self.zoom * 10  # шаг сетки
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
        """ ! Добавить виджет на поле
        @param widget: Виджет класса DraggableWidget
        """
        self.widgets.append(widget)

    def render_widgets(self):
        """! Отрисовывает все виджеты
        """
        for widget in self.widgets:
            widget.render_object()

    def set_zoom(self, zoom: int):
        w, h = self.parent.size().width(), self.parent.size().height()
        if zoom > self.zoom:
            self.pos = (int(self.pos[0] + 0.5 * (w - w * (self.zoom / zoom))),
                        int(self.pos[1] + 0.5 * (h - h * (self.zoom / zoom))))
        else:
            self.pos = (int(self.pos[0] + 0.5 * (w * (zoom / self.zoom) - w)),
                        int(self.pos[1] + 0.5 * (h * (zoom / self.zoom) - h)))
        self.zoom = zoom
        self.step = zoom * 10
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
            self.pos = (self.pos[0] + (self.cdx - QCursor.pos().x()) / self.zoom,
                        self.pos[1] + (self.cdy - QCursor.pos().y()) / self.zoom)
            self.cdx, self.cdy = QCursor.pos().x(), QCursor.pos().y()
            self.render_widgets()

