import pytest
import pytestqt
from Window import *
import sys
import os
from time import sleep
from LogicFunction import *

os.chdir("..")


def test_sgn_1():
    for i in range(1, 999):
        assert sgn(i) == 1


def test_sgn_2():
    for i in range(-999, 0):
        assert sgn(i) == -1


def test_sgn_0():
    assert sgn(0) == 0


def test_load_json():
    data = load_json("resources/elements/and.json")
    assert data['size'] == [5, 5]


def test_load_json_unreal():
    with pytest.raises(FileNotFoundError):
        load_json("foo.xd")

def test_window_start(qtbot):
    try:
        win = ProgramWindow()
    except Exception:
        pytest.fail("Window not working :(")


def test_window_buttons_1(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    qtbot.mouseClick(win.buttonTypeManual, Qt.LeftButton)


def test_window_buttons_2(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    qtbot.mouseClick(win.buttonGenerateFromTable, Qt.LeftButton)


def test_window_buttons_3(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    qtbot.mouseClick(win.buttonGenerateFromScheme, Qt.LeftButton)
    assert not win.schemeTab.isHidden()


def test_conversion_1(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)
    win.function = LogicFunction("A + A + B")
    win.conversion_selector.setCurrentIndex(0)
    qtbot.mouseClick(win.button_convert, Qt.LeftButton)
    assert win.conversion_log.toPlainText() == "F = A | A | B"


def test_conversion_2(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)
    win.function = LogicFunction("A + A + B")
    win.conversion_selector.setCurrentIndex(1)
    qtbot.mouseClick(win.button_convert, Qt.LeftButton)
    assert win.conversion_log.toPlainText() == "F = A + A + B"


def test_conversion_3(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)
    win.function = LogicFunction("A + A + B")
    win.conversion_selector.setCurrentIndex(2)
    qtbot.mouseClick(win.button_convert, Qt.LeftButton)
    assert win.conversion_log.toPlainText() == "F = A ⋁ A ⋁ B"


def test_conversion_4(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)
    win.function = LogicFunction("A + A + B")
    win.conversion_selector.setCurrentIndex(3)
    qtbot.mouseClick(win.button_convert, Qt.LeftButton)
    assert win.conversion_log.toPlainText() == "F = A or A or B"


def test_conversion_5(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)
    win.function = LogicFunction("A + A + B")
    win.conversion_selector.setCurrentIndex(4)
    qtbot.mouseClick(win.button_convert, Qt.LeftButton)
    assert win.conversion_log.toPlainText() == "F = A или A или B"


def test_conversions_6(qtbot):
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


def test_conversions_7(qtbot):
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


def test_conversions_8(qtbot):
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


def test_conversion_clear(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)
    win.function = LogicFunction("A + A + B")
    qtbot.mouseClick(win.button_convert, Qt.LeftButton)
    qtbot.mouseClick(win.conversion_clear, Qt.LeftButton)
    assert win.conversion_log.toPlainText() == ""