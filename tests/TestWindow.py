import json

import pytest
from unittest.mock import Mock
import pytestqt
from Window import *
import sys
import os
from time import sleep
from LogicFunction import *

os.chdir("..")


class TestUtility:
    def test_sgn_1(self):
        for i in range(1, 999):
            assert sgn(i) == 1

    def test_sgn_2(self):
        for i in range(-999, 0):
            assert sgn(i) == -1

    def test_sgn_0(self):
        assert sgn(0) == 0

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


class TestSchemeEditor:
    # тесты редактора схем (MySchemeCanvas+ProgramWindow)
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

    def test_scheme_load_1(self, qtbot):
        win = ProgramWindow()
        with pytest.raises(KeyError):
            win.canvas.load_scheme(load_json("tests/test_scheme_invalid_1.json"))

    def test_scheme_load_2(self, qtbot):
        win = ProgramWindow()
        with pytest.raises(TypeError):
            win.canvas.load_scheme(load_json("tests/test_scheme_invalid_2.json"))

    def test_scheme_load_3(self, qtbot):
        win = ProgramWindow()
        with pytest.raises(json.JSONDecodeError):
            win.canvas.load_scheme(load_json("tests/test_scheme_invalid_3.json"))

    def test_scheme_load_good(self, qtbot):
        win = ProgramWindow()
        win.canvas.load_scheme(load_json("tests/test_scheme_1.json"))

        assert len(win.canvas.widgets) == 4

    def test_scheme_save_1(self, qtbot):
        win = ProgramWindow()
        win.canvas.load_scheme(load_json("tests/test_scheme_1.json"))

        assert win.canvas.save_scheme() == load_json("tests/test_scheme_1.json")

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

    def test_init_render(self, qtbot):
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