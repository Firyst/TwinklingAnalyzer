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


class TestConversions:
    def test_conversion_1(self, qtbot):
        win = ProgramWindow()
        win.show()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(0)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A | A | B"

    def test_conversion_2(self, qtbot):
        win = ProgramWindow()
        win.show()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(1)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A + A + B"

    def test_conversion_3(self, qtbot):
        win = ProgramWindow()
        win.show()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(2)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A ⋁ A ⋁ B"

    def test_conversion_4(self, qtbot):
        win = ProgramWindow()
        win.show()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(3)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A or A or B"

    def test_conversion_5(self, qtbot):
        win = ProgramWindow()
        win.show()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        win.conversion_selector.setCurrentIndex(4)
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == "F = A или A или B"

    def test_conversions_6(self, qtbot):
        for i in range(5, 9):
            # смотрим, чтобы таблицы истинности для преобразованной и исходной совпадали
            win = ProgramWindow()
            win.show()
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
            win.show()
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
            win.show()
            qtbot.add_widget(win)
            default_f = LogicFunction("(A + B) * !(C ^ D)")
            win.function = default_f
            win.conversion_selector.setCurrentIndex(i)
            qtbot.mouseClick(win.button_convert, Qt.LeftButton)
            qtbot.mouseClick(win.conversion_save, Qt.LeftButton)
            assert win.function.generate_boolean_table() == default_f.generate_boolean_table()

    def test_conversion_clear(self, qtbot):
        win = ProgramWindow()
        win.show()
        qtbot.add_widget(win)
        win.function = LogicFunction("A + A + B")
        qtbot.mouseClick(win.button_convert, Qt.LeftButton)
        qtbot.mouseClick(win.conversion_clear, Qt.LeftButton)
        assert win.conversion_log.toPlainText() == ""


class TestSchemeEditor:
    # тесты редактора схем
    def test_scheme_open(self, qtbot):
        win = ProgramWindow()
        win.show()
        qtbot.add_widget(win)

        qtbot.mouseClick(win.buttonGenerateFromScheme, Qt.LeftButton)
        assert win.stackedWidget.currentIndex() == 1

    def test_scheme_close(self, qtbot):
        win = ProgramWindow()
        win.show()
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

