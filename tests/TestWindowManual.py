import pytest
import pytestqt
from Window import *
import sys
import os
from time import sleep
from LogicFunction import *


# открывает разные окна, их состояние нужно прооверять вручную

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
    # qtbot.mouseClick(win.action_about, Qt.LeftButton)