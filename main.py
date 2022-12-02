from PyQt5.QtWidgets import QApplication
import sys
from Window import ProgramWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ProgramWindow()
    ex.show()
    sys.exit(app.exec_())