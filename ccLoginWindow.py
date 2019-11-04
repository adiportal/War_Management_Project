# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loginWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import GUI
from Utility import in_use, init_cc_address, get_cc_send_address


class Ui_CompanyCommanderLogin(object):
    def setupUi(self, CompanyCommanderLogin):
        CompanyCommanderLogin.setObjectName("CompanyCommanderLogin")
        CompanyCommanderLogin.resize(252, 227)
        self.centralwidget = QtWidgets.QWidget(CompanyCommanderLogin)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 231, 171))
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 40, 71, 16))
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(20, 70, 41, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(20, 100, 41, 16))
        self.label_4.setObjectName("label_4")
        self.lineEdit_x_location = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_x_location.setGeometry(QtCore.QRect(100, 70, 51, 20))
        self.lineEdit_x_location.setObjectName("lineEdit_x_location")
        self.lineEdit_y_location = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_y_location.setGeometry(QtCore.QRect(100, 100, 51, 20))
        self.lineEdit_y_location.setObjectName("lineEdit_y_location")
        self.pushButton_login = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_login.setGeometry(QtCore.QRect(140, 140, 71, 21))
        self.pushButton_login.setStyleSheet("background-color: rgb(0, 209, 255);\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "background-color: rgb(0, 0, 127);")
        self.pushButton_login.setObjectName("pushButton_login")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(100, 40, 51, 21))
        self.comboBox.setObjectName("comboBox")
        CompanyCommanderLogin.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(CompanyCommanderLogin)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 252, 18))
        self.menubar.setObjectName("menubar")
        CompanyCommanderLogin.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(CompanyCommanderLogin)
        self.statusbar.setObjectName("statusbar")
        CompanyCommanderLogin.setStatusBar(self.statusbar)

        self.retranslateUi(CompanyCommanderLogin)
        QtCore.QMetaObject.connectSlotsByName(CompanyCommanderLogin)

        # Validation variables
        self.only_double = QtGui.QDoubleValidator()
        self.lineEdit_x_location.setValidator(self.only_double)
        self.lineEdit_y_location.setValidator(self.only_double)
        self.comboBox.addItems(['Choose:', '1', '2', '3'])

        self.pushButton_login.clicked.connect(self.on_click_login_button)

    def retranslateUi(self, CompanyCommanderLogin):
        _translate = QtCore.QCoreApplication.translate
        CompanyCommanderLogin.setWindowTitle(_translate("CompanyCommanderLogin", "Company Commander Login"))
        self.groupBox.setTitle(_translate("CompanyCommanderLogin", "Login"))
        self.label.setText(_translate("CompanyCommanderLogin", "<html><head/><body><p><span style=\" font-size:9pt;\">Company Number:</span></p></body></html>"))
        self.label_3.setText(_translate("CompanyCommanderLogin", "<html><head/><body><p><span style=\" font-size:9pt;\">X Location:</span></p></body></html>"))
        self.label_4.setText(_translate("CompanyCommanderLogin", "<html><head/><body><p><span style=\" font-size:9pt;\">Y Location:</span></p></body></html>"))
        self.pushButton_login.setText(_translate("CompanyCommanderLogin", "Login"))

    def on_click_login_button(self):

        # Setting variables from the inputs
        x_location_input = self.lineEdit_x_location.text()
        y_location_input = self.lineEdit_y_location.text()
        company_num_input = self.comboBox.currentText()

        # True/ False variables for validation
        correct_company_num = False
        correct_x_location = False
        correct_y_location = False
        cc_open = False

        # Checking validation and raising error message box if needed
        if company_num_input == 'Choose:':
            self.message_box("Please choose company number!")
        else:
            correct_company_num = True

        if x_location_input == '':
            self.message_box("Please fill your x location!")
        else:
            correct_x_location = True

        if y_location_input == '':
            self.message_box("Please fill your y location!")
        else:
            correct_y_location = True

        if in_use(get_cc_send_address(int(company_num_input))):
            self.message_box("The user is already open!")
        else:
            cc_open = True


        # If all conditions correct, the login window will be closed and the GUI will be open
        if correct_company_num is True and correct_x_location is True and correct_y_location is True and cc_open is True:
            location = (float(x_location_input), float(y_location_input))
            GUI.main(int(company_num_input), location)
            CompanyCommanderLogin.close()

    @staticmethod
    def message_box(message):
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Information)
        mb.setWindowTitle('Error')
        mb.setText(message)
        mb.setStandardButtons(QMessageBox.Ok)
        mb.exec_()


if __name__ == "__main__":
    import sys
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    CompanyCommanderLogin = QtWidgets.QMainWindow()
    ui = Ui_CompanyCommanderLogin()
    ui.setupUi(CompanyCommanderLogin)
    CompanyCommanderLogin.show()
    sys.exit(app.exec_())
    print()
