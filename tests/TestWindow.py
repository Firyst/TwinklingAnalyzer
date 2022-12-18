# -*- coding: utf-8 -*-

import pytest
import pytestqt
from Window import *
import os
from LogicFunction import *

os.chdir("..")


class TestUtility:
    def test_load_json(self):
        data = load_json("resources/elements/and.json")
        assert data['size'] == [5, 5]

    def test_load_json_unreal(self):
        with pytest.raises(FileNotFoundError):
            load_json("foo.xd")


"""
!!! ВНИМАНИЕ !!!
Код ниже выглядит немного страшно из-за создания нового окна в каждом тесте,
но это необходимо для корректной работы плагина QTBOT
"""


class TestConversions:
    def test_conversion_1(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(0)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A | A | B"

    def test_conversion_2(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(1)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A + A + B"

    def test_conversion_3(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(2)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A ⋁ A ⋁ B"

    def test_conversion_4(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(3)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A or A or B"

    def test_conversion_5(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(4)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A или A или B"

    def test_conversions_6(self, qtbot):
        for i in range(5, 9):
            # смотрим, чтобы таблицы истинности для преобразованной и исходной совпадали
            win = ProgramWindow()
            qtbot.add_widget(win)
            default_f = LogicFunction("A + A + B")
            win.function = default_f
            win.conversion_selector.setCurrentIndex(i)
            qtbot.mouseClick(win.button_convert, Qt.LeftButton)
            qtbot.mouseClick(win.conversion_save, Qt.LeftButton)
            assert win.function.generate_boolean_table() == default_f.generate_boolean_table()

    def test_conversions_7(self, qtbot):
        for i in range(5, 9):
            # смотрим, чтобы таблицы истинности для преобразованной и исходной совпадали
            win = ProgramWindow()
            qtbot.add_widget(win)
            default_f = LogicFunction("A * A * B")
            win.function = default_f
            win.conversion_selector.setCurrentIndex(i)
            qtbot.mouseClick(win.button_convert, Qt.LeftButton)
            qtbot.mouseClick(win.conversion_save, Qt.LeftButton)
            assert win.function.generate_boolean_table() == default_f.generate_boolean_table()

    def test_conversions_8(self, qtbot):
        for i in range(5, 9):
            # смотрим, чтобы таблицы истинности для преобразованной и исходной совпадали
            win = ProgramWindow()
            qtbot.add_widget(win)
            default_f = LogicFunction("(A + B) * !(C ^ D)")
            win.function = default_f
            win.conversion_selector.setCurrentIndex(i)
            qtbot.mouseClick(win.button_convert, Qt.LeftButton)
            qtbot.mouseClick(win.conversion_save, Qt.LeftButton)
            assert win.function.generate_boolean_table() == default_f.generate_boolean_table()

    def test_conversion_clear(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        qtbot.mouseClick(win.conversion_clear, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == ""

    def test_window_missing_func(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)

        qtbot.mouseClick(win.conversion_save, Qt.LeftButton)

        assert win.conversion_log.toPlainText() == ''


class TestCanvas:
    # MySchemeCanvas tests
    def test_init(self, qtbot):
        canvas = MySchemeCanvas(QLabel())

        assert len(canvas.widgets) == len(canvas.lines) == len(canvas.connectors) == 0

    def test_new(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        canvas.new_widget(DraggableWidget(parent, "output", canvas))

        assert len(canvas.widgets) == 1 and len(canvas.connectors) == 1

    def test_new_2(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        canvas.new_widget(DraggableWidget(parent, "and", canvas))

        assert len(canvas.widgets) == 1 and len(canvas.connectors) == 3 and (len(canvas.lines)) == 0

    def test_new_3(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        canvas.new_widget(DraggableWidget(parent, "and", canvas))
        canvas.new_line(Connection(canvas, (10, 10), (20, 10)))
        Connection2(canvas, (10, 10), (12, 12))

        assert len(canvas.widgets) == 1 and len(canvas.connectors) == 9 and (len(canvas.lines)) == 3

    def test_connectors(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        canvas.new_widget(DraggableWidget(parent, "output", canvas))

        cons = canvas.compile_connectors()

        assert sorted(list(cons.keys())) == [(0, 1)]

    def test_connectors_2(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        canvas.new_widget(DraggableWidget(parent, "and", canvas))
        Connection2(canvas, (0, 1), (0, 3))  # weird but ok

        cons = canvas.compile_connectors()

        assert sorted(list(cons.keys())) == [(0, 1), (0, 3), (4, 2)]

    def test_connectors_3(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        canvas.new_widget(DraggableWidget(parent, "and", canvas))
        Connection2(canvas, (0, 1), (0, 4))  # weird but ok

        cons = canvas.compile_connectors()

        assert sorted(list(cons.keys())) == [(0, 1), (0, 3), (0, 4), (4, 2)]

    def test_render(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        widget = canvas.new_widget(DraggableWidget(parent, "output", canvas))

        canvas.move_field(-100, -100)

        assert widget.geometry().x() == 100 and widget.geometry().y() == 100

    def test_render_2(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        widget = canvas.new_widget(DraggableWidget(parent, "output", canvas))
        widget.grid_pos = (2, 3)

        canvas.move_field(-100, -100)

        assert widget.geometry().x() == 140 and widget.geometry().y() == 160

    def test_render_3(self, qtbot):
        parent = QLabel()
        parent.setGeometry(0, 0, 240, 240)
        canvas = MySchemeCanvas(parent)
        widget = canvas.new_widget(DraggableWidget(parent, "output", canvas))
        widget.grid_pos = (3, 3)

        canvas.set_zoom(2)

        assert widget.geometry() == QtCore.QRect(0, 0, 120, 120)

    def test_render_4(self, qtbot):
        parent = QLabel()
        parent.setGeometry(0, 0, 240, 240)
        canvas = MySchemeCanvas(parent)
        widget = canvas.new_widget(DraggableWidget(parent, "output", canvas))
        widget.grid_pos = (4, 4)

        canvas.set_zoom(2)

        assert widget.geometry() == QtCore.QRect(40, 40, 120, 120)

    def test_compilation(self, qtbot):
        parent = QLabel()
        parent.setGeometry(0, 0, 240, 240)
        canvas = MySchemeCanvas(parent)

        # add some widgets
        widget = canvas.new_widget(DraggableWidget(parent, "output", canvas))
        widget.grid_pos = (12, 4)

        widget = canvas.new_widget(DraggableWidget(parent, "and", canvas))
        widget.grid_pos = (6, 3)

        Connection2(canvas, (10, 5), (12, 5))

        widget = canvas.new_widget(DraggableWidget(parent, "input", canvas, "A"))
        widget.grid_pos = (0, 3)

        Connection2(canvas, (2, 4), (6, 4))

        widget = canvas.new_widget(DraggableWidget(parent, "input", canvas, "B"))
        widget.grid_pos = (0, 5)

        Connection2(canvas, (2, 6), (6, 6))

        canvas.render_widgets()

        assert canvas.compile_scheme().exp == "(A and B)"

    def test_compilation_2(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        widget = canvas.new_widget(DraggableWidget(parent, "output", canvas))

        with pytest.raises(SchemeCompilationError):
            canvas.compile_scheme()

    def test_compilation_3(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        widget = canvas.new_widget(DraggableWidget(parent, "output", canvas))
        Connection2(canvas, (-2, -2), (0, 1))
        Connection2(canvas, (-2, 4), (0, 1))

        with pytest.raises(SchemeCompilationError):
            canvas.compile_scheme()

    def test_scheme_load_1(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        with pytest.raises(KeyError):
            canvas.load_scheme(load_json("tests/test_scheme_invalid_1.json"))

    def test_scheme_load_2(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        with pytest.raises(TypeError):
            canvas.load_scheme(load_json("tests/test_scheme_invalid_2.json"))

    def test_scheme_load_3(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        with pytest.raises(json.JSONDecodeError):
            canvas.load_scheme(load_json("tests/test_scheme_invalid_3.json"))

    def test_scheme_load_good(self, qtbot):
        parent = QLabel()
        canvas = MySchemeCanvas(parent)
        canvas.load_scheme(load_json("tests/test_scheme_1.json"))

        assert len(canvas.widgets) == 4

    def test_scheme_save_1(self, qtbot):
        win = ProgramWindow()
        win.canvas.load_scheme(load_json("tests/test_scheme_1.json"))

        assert win.canvas.save_scheme() == load_json("tests/test_scheme_1.json")


class TestSchemeEditor:
    # тесты редактора схем в окружении программы (MySchemeCanvas+ProgramWindow)
    def test_scheme_open(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)

        qtbot.mouseClick(win.buttonGenerateFromScheme, Qt.LeftButton)
        assert win.stackedWidget.currentIndex() == 1

    def test_scheme_close(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)

        qtbot.mouseClick(win.buttonGenerateFromScheme, Qt.LeftButton)
        win.action_scheme_quit.trigger()
        assert win.stackedWidget.currentIndex() == 0

    def test_add_widgets(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)
        qtbot.mouseClick(win.buttonGenerateFromScheme, Qt.LeftButton)
        test_widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))
        test_line = Connection(win.canvas, (10, 10), (10, 20), 0)

        assert test_widget in win.canvas.widgets and len(win.canvas.connectors) == 6

    def test_clear_canvas(self, qtbot):
        win = ProgramWindow()
        qtbot.add_widget(win)
        qtbot.mouseClick(win.buttonGenerateFromScheme, Qt.LeftButton)
        win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))
        win.canvas.clear_all()

        assert len(win.canvas.widgets) == 0

    def test_scheme_compile_1(self, qtbot):
        win = ProgramWindow()
        win.canvas.load_scheme(load_json("tests/test_scheme_1.json"))

        assert win.canvas.compile_scheme().exp == '(A and B)'

    def test_scheme_complie_2(self, qtbot):
        win = ProgramWindow()
        with pytest.raises(SchemeCompilationError):
            win.canvas.compile_scheme()


class TestDraggableWidget:
    def test_init(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "not", win.canvas))

        assert widget.get_grid_pos() == (0, 0)

    def test_connectors(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "not", win.canvas))

        assert len(win.canvas.connectors) == 3

    def test_connectors_2(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))

        assert len(win.canvas.connectors) == 4

    def test_set_pos(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))
        widget.set_pos(99, 99)

        assert widget.geometry().x() == 99 and widget.geometry().y() == 99

    def test_set_and_get_size(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))
        widget.set_size(111, 111)

        assert widget.get_size() == (111, 111)

    def test_render(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "not", win.canvas))
        widget.grid_pos = (6, 10)
        win.canvas.pos = (100, 100)
        widget.render_object()

        assert (widget.geometry().x(), widget.geometry().y(), widget.geometry().width(), widget.geometry().height()) \
               == (20, 100, 100, 60)

    def test_render_2(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))
        widget.grid_pos = (6, 10)
        win.canvas.pos = (100, 100)
        widget.render_object()

        assert (widget.geometry().x(), widget.geometry().y(), widget.geometry().width(), widget.geometry().height()) \
               == (20, 100, 100, 100)

    def test_render_3(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.set_zoom(2)
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "not", win.canvas))
        widget.grid_pos = (6, 10)
        win.canvas.pos = (100, 100)
        widget.render_object()

        assert (widget.geometry().x(), widget.geometry().y(), widget.geometry().width(), widget.geometry().height()) \
               == (40, 200, 200, 120)

    def test_repr(self):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))
        widget.grid_pos = (11, 11)

        assert "lObject((11, 11), and)" == str(widget)


class TestConnector:
    def test_init(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        parent = win.canvas.new_widget(DraggableWidget(win.schemeTab, "not", win.canvas))  # init called inside

        assert sorted(list(map(lambda x: x.get_grid_pos(), parent.connectors))) == [(0, 1), (4, 1)]

    def test_init_2(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        parent = win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))  # init called inside

        assert sorted(list(map(lambda x: x.get_grid_pos(), parent.connectors))) == [(0, 1), (0, 3), (4, 2)]

    def test_init_3(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        parent = win.canvas.new_line(Connection(win.canvas, (1, 1), (8, 1), 0))  # init called inside

        assert sorted(list(map(lambda x: x.get_grid_pos(), win.canvas.connectors))) == [(1, 1), (8, 1)]

    def test_move(self, qtbot):
        # connector should automatically follow its parent
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        parent = win.canvas.new_widget(DraggableWidget(win.schemeTab, "and", win.canvas))
        parent.grid_pos = (3, 3)
        parent.render_object()

        assert sorted(list(map(lambda x: x.get_grid_pos(), parent.connectors))) == [(3, 4), (3, 6), (7, 5)]

    def test_render(self, qtbot):
        # connector should change size depending on zoom
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()
        win.canvas.set_zoom(2)

        parent = win.canvas.new_widget(DraggableWidget(win.schemeTab, "not", win.canvas))
        parent.render_object()

        assert parent.connectors[0].geometry().width() == parent.connectors[0].geometry().height() == \
               parent.connectors[1].geometry().width() == parent.connectors[1].geometry().height() == 40

    def test_repr(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()
        win.canvas.set_zoom(2)

        parent = win.canvas.new_widget(DraggableWidget(win.schemeTab, "not", win.canvas))
        parent.grid_pos = (1, 1)
        parent.render_object()

        assert "Connector((1, 2), in1)" == str(parent.connectors[0])


class TestConnection:
    def test_init(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        line = win.canvas.new_line(Connection(win.canvas, (0, 0), (2, 0), 0))  # init called inside

        assert sorted(list(map(lambda x: x.get_grid_pos(), win.canvas.connectors))) == [(0, 0), (2, 0)]

    def test_init_2(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        line = win.canvas.new_line(Connection(win.canvas, (0, 0), (0, 2), 1))  # init called inside

        assert sorted(list(map(lambda x: x.get_grid_pos(), win.canvas.connectors))) == [(0, 0), (0, 2)]

    def test_render(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        line = win.canvas.new_line(Connection(win.canvas, (0, 0), (2, 2), 0))  # init called inside
        line.render_line()

        assert sorted(list(map(lambda x: x.get_grid_pos(), win.canvas.connectors))) == [(0, 0), (2, 0)]

    def test_render_2(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        line = win.canvas.new_line(Connection(win.canvas, (0, 0), (2, 2), 1))  # init called inside
        line.render_line()

        assert sorted(list(map(lambda x: x.get_grid_pos(), win.canvas.connectors))) == [(0, 0), (0, 2)]

    def test_init_delete(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        line = win.canvas.new_line(Connection(win.canvas, (0, 0), (2, 2), 1))  # init called inside
        line.delete()

        assert len(win.canvas.connectors) == 0

    def test_repr(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        widget = win.canvas.new_line(Connection(win.canvas, (2, 2), (2, 8), 1))

        assert "Line((2, 2), (2, 8))" == str(widget)


class TestConnection2:
    def test_init_1(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        Connection2(win.canvas, (1, 1), (4, 4))
        assert len(win.canvas.lines) == 2 and len(win.canvas.connectors) == 4

    def test_init_2(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        Connection2(win.canvas, (1, 1), (1, 4))
        assert len(win.canvas.lines) == 1 and len(win.canvas.connectors) == 2

    def test_init_3(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        Connection2(win.canvas, (1, 1), (4, 1))
        assert len(win.canvas.lines) == 1 and len(win.canvas.connectors) == 2

    def test_render_1(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        Connection2(win.canvas, (1, 1), (4, 4))
        cons = win.canvas.compile_connectors()
        # проверка, что линия соеденилась
        assert len(max(cons.values(), key=len)) == 2

    def test_render_2(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        Connection2(win.canvas, (1, 1), (1, 4))
        cons = win.canvas.compile_connectors()
        # проверка, что линия одна
        assert len(max(cons.values(), key=len)) == 1

    def test_render_3(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        Connection2(win.canvas, (1, 1), (1, 4))
        Connection2(win.canvas, (1, 1), (4, 1))
        Connection2(win.canvas, (4, 1), (4, 4))
        Connection2(win.canvas, (1, 4), (4, 4))
        cons = win.canvas.compile_connectors()
        # проверка квадрата
        assert sum(map(len, cons.values())) == 8

    def test_delete(self, qtbot):
        win = ProgramWindow()
        win.open_scheme_editor()
        win.canvas.clear_all()

        line = Connection2(win.canvas, (1, 1), (4, 4))
        line.delete()
        assert len(win.canvas.lines) == 0 and len(win.canvas.connectors) == 0