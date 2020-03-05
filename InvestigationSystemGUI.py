import sys
import threading
import time
from datetime import datetime, timedelta
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import matplotlib.pyplot as plt
import Entities
import Utility
from Entities import Soldier
from Utility import EnemyType, SpeedButtons
from map_key import Ui_MainWindow


class MatplotlibWidget(QMainWindow):
    soldiers = []
    enemies = []
    company_commanders = []
    cc_scenarios = []
    field_scenario = None
    frames = None
    play = False

    def __init__(self, cc1_path=None, cc2_path=None, cc3_path=None, field_path=None):
        self.set_pathes(cc1_path, cc2_path, cc3_path, field_path)
        self.field_scenario.fix_frames()
        self.frames = self.field_scenario.get_frames()

        QMainWindow.__init__(self)

        loadUi("timeslider.ui", self)

        self.console.setReadOnly(True)
        self.cursor = QTextCursor(self.console.document())

        self.slider.setMinimum(0)
        self.slider.setMaximum(self.field_scenario.get_time_in_sec())
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.value_changed)
        self.current_time.setText(self.frames[0].get_time())
        self.val = self.slider.value()
        self.time_sleep = None
        self.pause_button.setDown(True)

        self.setWindowTitle("Example GUI")
        self.map_key_button.clicked.connect(self.map_key_window)

        self.play_button.clicked.connect(self.play_thread)
        self.pause_button.clicked.connect(self.pause_press)

        self.update_graph()

    def set_pathes(self, cc1_path, cc2_path, cc3_path, field_path):
        cc_path_list = [cc1_path, cc2_path, cc3_path]

        for path in cc_path_list:
            if path != "None":
                cc_scenario = Utility.load("CompanyCommanderScenarios/" + str(path))
                self.cc_scenarios.append(cc_scenario)

        self.field_scenario = Utility.load("FieldScenarios/" + str(field_path))

    def map_key_window(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()

    def update_graph(self):
        self.MplWidget.canvas.axes.set_xlim(0, 25)
        self.MplWidget.canvas.axes.set_ylim(0, 15)
        self.MplWidget.canvas.axes.clear()
        img = plt.imread("MAP.png")
        self.MplWidget.canvas.axes.imshow(img, extent=[0, 25, 0, 15])
        self.create_plot_new(self.soldiers, self.enemies, self.company_commanders)
        self.MplWidget.canvas.draw()

    def create_plot_new(self, soldiers, enemies, company_commanders):
        # self.MplWidget.canvas.axes.get_yaxis().set_visible(False)
        # self.MplWidget.canvas.axes.get_xaxis().set_visible(False)

        x = []
        y = []
        color = []
        marker = []
        sizes = []

        for soldier in soldiers:
            x.append(soldier.x)
            y.append(soldier.y)
            if type(soldier) == Soldier:
                marker.append('o')
                sizes.append(4)
            else:
                marker.append('*')
                sizes.append(8)

            if soldier.company_number == 1:
                color.append("cyan")
            elif soldier.company_number == 2:
                color.append('orange')
            else:
                color.append('lime')

        for x_field, y_field, color_field, marker_field, size_field in zip(x, y, color, marker, sizes):
            self.MplWidget.canvas.axes.plot([x_field], [y_field], color=color_field, marker=marker_field,
                                            markersize=size_field, picker=10)

        e_x = []
        e_y = []
        e_marker = []

        for enemy in enemies:
            e_x.append(enemy.x)
            e_y.append(enemy.y)

            if enemy.get_type() == EnemyType.soldier.value:
                e_marker.append("o")

            elif enemy.get_type() == EnemyType.launcher.value:
                e_marker.append("^")

            else:
                e_marker.append("s")

            for x, y, m in zip(e_x, e_y, e_marker):
                self.MplWidget.canvas.axes.plot([x], [y], color="red", marker=m, markersize=7,
                                                markeredgecolor="black", picker=5)

        cc_x = []
        cc_y = []
        cc_color = []

        for cc in company_commanders:
            if cc is not None:
                cc_x.append(cc.company_commander.x)
                cc_y.append(cc.company_commander.y)
                if cc.company_num == 1:
                    cc_color.append("cyan")
                elif cc.company_num == 2:
                    cc_color.append("orange")
                else:
                    cc_color.append("lime")

        for x, y, color in zip(cc_x, cc_y, cc_color):
            self.MplWidget.canvas.axes.plot([x], [y], color="black", marker="o", markersize=7, markeredgecolor=color,
                                            markeredgewidth=1.5)

    def value_changed(self):
        index = self.slider.value()
        self.val = index
        self.current_time.setText(self.frames[index].get_time())
        if index == 0:
            self.soldiers = []
            self.enemies = []
            self.company_commanders = []
            self.update_graph()

        else:
            self.frame = self.frames[index - 1]
            self.soldiers = self.frame.get_forces()
            self.enemies = self.frame.get_enemies()
            self.company_commanders = self.cc_scenarios
            self.update_graph()
            self.set_console(self.frame.get_time())

    def set_console(self, date_time_str):
        self.console.clear()
        date_time = datetime.strptime(date_time_str, "%H:%M:%S")
        current_time = datetime.strptime(self.field_scenario.get_start_time(), "%H:%M:%S")

        while current_time <= date_time:
            field_message = self.field_scenario.get_message(datetime.strftime(current_time, "%H:%M:%S"))
            if len(field_message) > 0:
                for message in field_message:
                    self.console.insertHtml(message.get_colored_msg())
                    self.console.moveCursor(QTextCursor.End)

            for cc in self.cc_scenarios:
                if cc is None:
                    continue

                cc_message = cc.get_message(datetime.strftime(current_time, "%H:%M:%S"))
                if len(cc_message) > 0:
                    for message in cc_message:
                        self.console.insertHtml(message.get_colored_msg())
                        self.console.moveCursor(QTextCursor.End)

            current_time += timedelta(seconds=1)

    def play_press(self):
        while self.play:
            self.pause_button.setDown(False)
            self.play_button.setDown(True)
            speed = self.radio_button_checked()

            if speed == SpeedButtons.normal.value:
                self.time_sleep = 1

            elif speed == SpeedButtons.x2.value:
                self.time_sleep = 0.5

            elif speed == SpeedButtons.x4.value:
                self.time_sleep = 0.25

            else:
                pass

            self.val += 1
            self.slider.setValue(self.val)
            time.sleep(self.time_sleep)

        self.pause_button.setDown(True)
        self.play_button.setDown(False)

    def play_thread(self):
        self.play = True
        self.pause_button.setDown(False)
        self.play_button.setDown(True)
        play = threading.Thread(target=self.play_press)
        play.start()

    def pause_press(self):
        self.play = False
        self.pause_button.setDown(True)
        self.play_button.setDown(False)

    def radio_button_checked(self):
        if self.normal_speed.isChecked():
            return SpeedButtons.normal.value

        elif self.speed2.isChecked():
            return SpeedButtons.x2.value

        elif self.speed4.isChecked():
            return SpeedButtons.x4.value

        else:
            pass


cc1_path = sys.argv[1]
cc2_path = sys.argv[2]
cc3_path = sys.argv[3]
field_path = sys.argv[4]
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
app = QApplication([])
window = MatplotlibWidget(cc1_path, cc2_path, cc3_path, field_path)
window.show()
app.exec_()
