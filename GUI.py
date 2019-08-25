import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(500, 300))
        self.setWindowTitle("Example")

        button = QPushButton('Click me', self)  # Creates an object of the type QPushButton
        button.clicked.connect(self.clickMethod)
        button.resize(100, 32)
        button.move(200, 100)

    def clickMethod(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(300, 200))
        self.setWindowTitle("Example2")
        label = QLabel('Hello World!', self)
        label.show()
        self.show()


if __name__ == "__main__":  # When python runs a program the value of __name__ is __main__
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
