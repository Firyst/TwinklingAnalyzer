# -*- coding: utf-8 -*-

import pytestqt
import os
from Dialogs import *


os.chdir('..')


class TestInputDialog:
    def test_1(self, qtbot):
        # test works
        dialog = InputDialog()
        dialog.show()
        dialog.close_dialog()
        assert dialog.output is None

    def test_2(self, qtbot):
        dialog = InputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonCancel, Qt.LeftButton)
        assert dialog.output is None

    def test_3(self, qtbot):
        # manual test - requires input
        dialog = InputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_4(self, qtbot):
        # manual test - unknown symbol
        dialog = InputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.inputFunction.setText("???")
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_5(self, qtbot):
        # manual test - bad function
        dialog = InputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.inputFunction.setText(")))")
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_6(self, qtbot):
        # manual test - bad function 2
        dialog = InputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.inputFunction.setText("a + b + c))))))")
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_7(self, qtbot):
        # manual test - good function
        dialog = InputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.inputFunction.setText("a + b * c")
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output.exp == "a or b and c"


class TestConfirmDialog:
    def test_1(self, qtbot):
        # test working
        dialog = ConfirmDialog("test", "test")
        dialog.show()
        dialog.close_dialog()
        assert dialog.output is None and (dialog.windowTitle() == "test") and (dialog.label.text() == "test")

    def test_2(self, qtbot):
        dialog = ConfirmDialog("test", "test")
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonCancel, Qt.LeftButton)
        assert dialog.output is None

    def test_3(self, qtbot):
        dialog = ConfirmDialog("test", "test")
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output


class TestTinyInputDialog:
    def test_1(self, qtbot):
        # test works
        dialog = TinyInputDialog()
        dialog.show()
        dialog.close_dialog()
        assert dialog.output is None

    def test_2(self, qtbot):
        dialog = TinyInputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonCancel, Qt.LeftButton)
        assert dialog.output is None

    def test_3(self, qtbot):
        # manual test - requires input
        dialog = TinyInputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_4(self, qtbot):
        # manual test - unknown symbol
        dialog = TinyInputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.inputLine.setText("???")
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_5(self, qtbot):
        # manual test - bad name
        dialog = TinyInputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.inputLine.setText("NoT")
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_6(self, qtbot):
        # manual test - starting with number
        dialog = TinyInputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.inputLine.setText("00x")
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_7(self, qtbot):
        # manual test - good
        dialog = TinyInputDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.inputLine.setText("VAR")
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output == 'VAR'


class TestWarnDialog:
    # very simple..
    def test_1(self, qtbot):
        # test working
        dialog = WarnDialog("test", "test2")
        dialog.show()
        dialog.close_dialog()
        assert (dialog.windowTitle() == "test") and (dialog.mainLabel.text() == "test2")

    def test_2(self, qtbot):
        dialog = WarnDialog("test", "test")
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.isHidden()


class TestTableDialog:
    def test_1(self, qtbot):
        dialog = TableDialog()
        dialog.show()
        dialog.close_dialog()
        assert dialog.output is None

    def test_2(self, qtbot):
        dialog = TableDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonCancel, Qt.LeftButton)
        assert dialog.output is None

    def test_3(self, qtbot):
        # test table changes
        dialog = TableDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.varSelector.setCurrentIndex(4)
        dialog.draw_table()

        qtbot.mouseClick(dialog.buttonCancel, Qt.LeftButton)
        assert dialog.tableWidget.rowCount() == 64

    def test_4(self, qtbot):
        # manual test not enough value
        dialog = TableDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_5(self, qtbot):
        # manual test bad value
        dialog = TableDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.tableWidget.setItem(0, 2, QTableWidgetItem("bad value >:)"))
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output is None

    def test_6(self, qtbot):
        # test ok value
        dialog = TableDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        for i in range(4):
            dialog.tableWidget.setItem(i, 2, QTableWidgetItem(str(i % 2)))
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output.exp == "(a or b) and (not a or b)"

    def test_7(self, qtbot):
        # test ok value 2 - another method
        dialog = TableDialog()
        dialog.show()
        qtbot.add_widget(dialog)
        dialog.methodSelector.setCurrentIndex(1)
        for i in range(4):
            dialog.tableWidget.setItem(i, 2, QTableWidgetItem(str(i // 3)))
        qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
        assert dialog.output.exp == "a and b"


class TestLogicDialog:
    def test_1(self, qtbot):
        # test works
        dialog = LogicSelectDialog()
        dialog.show()
        dialog.close_dialog()
        assert dialog.output is None

    def test_2(self, qtbot):
        # test confirm
        for i, e in enumerate(('not', 'and', 'or', 'xor', 'input')):
            dialog = LogicSelectDialog()
            dialog.show()
            qtbot.add_widget(dialog)
            dialog.selector.setCurrentIndex(i)
            qtbot.mouseClick(dialog.buttonConfirm, Qt.LeftButton)
            assert dialog.output == e