import sys
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog, QPushButton
from Dialogs import InputDialog, WarnDialog, TableDialog


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
        self.canvas.new_widget(DraggableWidget(self.schemeTab, 'debug'))
        self.canvas.new_widget(DraggableWidget(self.schemeTab, 'debug'))
        self.wheelEvent = self.canvas.scroll

    def debug_canvas(self):
        pass

    def create_canvas_layout(self):
        pass

    def canvas_mouse_event(self, ev):
        print(ev.x(), ev.y())

    # create methods
    def createFunctionManual(self):
        dialog = InputDialog()
        dialog.exec_()

    def createFunctionFromScheme(self):
        dialog = WarnDialog("Ошибка", "Рисунок некорректный")
        dialog.exec_()

    def createFunctionFromTable(self):
        dialog = TableDialog()
        dialog.exec_()



class DraggableWidget(QLabel):
    def __init__(self, parent: QWidget, object_type: str):
        """! Создать виджет объекта схемы
        @param object_type: тип картинки. Возможные значения: and2, or2, not, inp, out, xor, debug
        """
        super().__init__(parent)
        self.cdx, self.cdy, self.drag = 0, 0, 0  # разница между позицией объект и местом нажатия курсора
        self.grid_size = 10  # размер сетки. изменяется при увеличении/уменьшении

        self.setScaledContents(True)
        if object_type == 'debug':
            self.setPixmap(QPixmap("resources/test.png"))

        self.set_size(50, 50)

    def set_pos(self, x: int, y: int):
        self.setGeometry(x, y, self.geometry().width(), self.geometry().height())

    def set_size(self, w: int, h: int):
        self.setGeometry(self.geometry().x(), self.geometry().y(), w, h)
        #new_pix = QPixmap("resources/test.png")
        self.pixmap().scaled(w, h, Qt.KeepAspectRatio)

        # self.setPixmap(new_pix)

    def get_pos_c(self):
        '''! Получить координаты центра объекта
        @return: tuple(x, y)
        '''
        return (self.geometry().x() + self.geometry().width() // 2, self.geometry().y() + self.geometry().height() // 2)

    def get_size(self):
        return (self.geometry().width(), self.geometry().height())

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        print('press')
        self.cdx, self.cdy = self.x() - QCursor.pos().x(), self.y() - QCursor.pos().y()

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        print('release')

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        print(ev.x(), ev.y(), QCursor.pos())
        self.set_pos((QCursor.pos().x() + self.cdx), (QCursor.pos().y() + self.cdy))
        pass


class MySchemeCanvas:

    def __init__(self, parent):
        self.parent = parent
        self.widgets = list()  # all widget on canvas
        self.lines = list()  # all lines on canvas
        self.connections = list()
        self.zoom = 1

    def new_widget(self, widget: DraggableWidget):
        self.widgets.append(widget)

    def set_zoom(self, zoom: int):
        coords = self.parent.mapFromGlobal(QCursor.pos())
        if zoom < 1 or zoom > 10:
            raise ValueError("Некорректное приближение. Используйте число 1-10")

        delta = zoom / self.zoom # во сколько раз все увеличивается
        for widg in self.widgets:
            widg.set_pos(coords.x() + round((widg.x() - coords.x()) * delta), coords.y() +
                         round((widg.y() - coords.y()) * delta))
            widg.set_size(int(widg.get_size()[0] * delta), int(widg.get_size()[1] * delta))
            widg.grid_size = 10 * zoom
        self.zoom = zoom

    def scroll(self, event: QtGui.QWheelEvent):
        scr_x, scr_y = event.pixelDelta().x(), event.pixelDelta().y()
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            # приближение
            if scr_y > 0:
                self.set_zoom(min(10, self.zoom + 1))
            elif scr_y < 0:
                self.set_zoom(max(self.zoom - 1, 1))
            return
        elif modifiers == Qt.AltModifier:
            # горизонтальный скролл
            scr_x, scr_y = scr_y, scr_x

        # навигация по полю
        for widg in self.widgets:
            widg.set_pos(widg.x() + scr_x, widg.y() + scr_y)
