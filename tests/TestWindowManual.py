# -*- coding: utf-8 -*-

import pytest
import pytestqt
from Window import *
import os

# открывает разные окна, их состояние нужно прооверять вручную :(

os.chdir("..")


def test_window_buttons_1(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    qtbot.mouseClick(win.buttonTypeManual, Qt.LeftButton)


def test_window_buttons_2(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    qtbot.mouseClick(win.buttonGenerateFromTable, Qt.LeftButton)


def test_window_actions_1(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)
    win.action_about.trigger()


def test_window_missing_func(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    qtbot.mouseClick(win.button_convert, Qt.LeftButton)


def test_window_missing_func_2(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    qtbot.mouseClick(win.button_analyze_generate, Qt.LeftButton)


def test_window_missing_func_3(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    qtbot.mouseClick(win.button_analyze_save, Qt.LeftButton)


def test_clear(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    win.canvas.load_scheme(load_json("tests/test_scheme_1.json"))
    win.action_scheme_clear.trigger()

    assert len(win.canvas.widgets) == 1


def test_compile(qtbot):
    win = ProgramWindow()
    qtbot.add_widget(win)

    win.canvas.load_scheme(load_json("tests/test_scheme_1.json"))

    win.action_scheme_compile.trigger()

    assert win.function.exp == "(A and B)"
