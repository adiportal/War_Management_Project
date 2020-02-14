# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timeslider.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!
import linecache
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

class Logtime:
    def __init__(self):
        file_name = 'FieldLog.log'

        num_of_lines = self.file_len('FieldLog.log')
        print(num_of_lines)

        file = open('FieldLog.log', 'r')

        first_line = linecache.getline(file_name, 1)
        last_line = linecache.getline(file_name, num_of_lines)
        print(first_line)
        print(last_line)

        begin_time = first_line[0:19]
        begin = datetime.datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
        end_time = last_line[0:19]
        end = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        print(begin)
        print(end)

        self.time = end - begin
        self.time_in_sec = self.time.seconds
        print("time:", self.time)
        print(self.time.seconds)

    def file_len(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        log_time = Logtime()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(507, 401)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(30, 110, 461, 20))
        self.horizontalSlider.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(log_time.time_in_sec)
        self.horizontalSlider.setPageStep(10)
        self.horizontalSlider.setProperty("value", 55)
        self.horizontalSlider.setTracking(True)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setInvertedAppearance(False)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setValue(0)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(100, 150, 261, 111))
        self.plainTextEdit.setObjectName("plainTextEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 507, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.horizontalSlider.valueChanged.connect(self.value_change)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def value_change(self):
        my_value = self.horizontalSlider.value()
        time = datetime.datetime(2020, 11, 28, 00, 00, 00) + datetime.timedelta(seconds=my_value)
        self.plainTextEdit.setPlainText(str(time.strftime("%H:%M:%S")))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
