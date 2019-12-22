import sys
import threading
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import BattalionCommander
from Entities import Soldier, APC
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import numpy as np
from Utility import create_move_to_message, EnemyType


class MatplotlibWidget(QMainWindow):
    soldiers = []  # company1 list from the 3 lists of the company commander
    enemies = []
    company_commanders = []

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi("battalion_commander.ui", self)

        self.setWindowTitle("Battalion Commander")

        self.tooltip_visible = False
        self.tooltip_coords = 0, 0
        self.tooltip_text = ''

        # Starting the animation using the animate function, update every 1000 miliseconds
        self.ani = FuncAnimation(self.MplWidget.canvas.figure, self.animate, interval=1000, blit=False)

        # Starting the hover event (on hovering a marker an informative label shows up)
        self.MplWidget.canvas.mpl_connect("motion_notify_event", self.on_hover)

        self.enemies_checkBox.setChecked(True)
        self.company1_checkbox.setChecked(True)
        self.company2_checkbox.setChecked(True)
        self.company3_checkbox.setChecked(True)

    # def closeEvent(self, event):
    #     reply = QMessageBox.question(
    #         self, "Message",
    #         "Are you sure you want to quit? Any unsaved work will be lost.",
    #         QMessageBox.Close | QMessageBox.Cancel
    #         )
    #     if reply == QMessageBox.Close:
    #         CompanyCommanderUDP.STOP_CC_THREADS = True
    #
    #     else:
    #         event.ignore()

    # function for a thread, updates the soldiers list
    def update_field(self):
        while True:
            self.soldiers = BattalionCommander.company1 + BattalionCommander.company2 + BattalionCommander.company3
            self.company_commanders = BattalionCommander.battalion_commander.commanders
            self.enemies = BattalionCommander.battalion_commander.enemies
            # print("gui", len(self.company_commanders))
            time.sleep(2.0)

        # function for the FuncAnimation option, clears and create the plot again

    def animate(self, i):
        self.MplWidget.canvas.axes.clear()
        img = plt.imread("MAP.png")
        self.MplWidget.canvas.axes.imshow(img)
        self.MplWidget.canvas.axes.imshow(img, extent=[0, 25, 0, 15])
        # Starting the properties of the marker's labels
        self.tooltip = self.MplWidget.canvas.axes.annotate(self.tooltip_text, self.tooltip_coords,
                                                           xytext=self.set_xy_text(self.tooltip_coords),
                                                           textcoords="offset points",
                                                           ha=self.set_ha_value(self.set_xy_text(self.tooltip_coords)),
                                                           va=self.set_va_value(self.set_xy_text(self.tooltip_coords)),
                                                           size=6,
                                                           bbox=dict(facecolor='wheat', boxstyle="round", alpha=0.8),
                                                           arrowprops=dict(shrink=15, facecolor='black', width=3,
                                                                           headlength=8))
        self.tooltip.set_visible(self.tooltip_visible)  # Set the visibility of the label according to its current mode
        self.create_plot()

    def set_xy_text(self, coords):  # function to help set the position of the text in the label according to the
        # location of the marker in the plot
        self.MplWidget.canvas.axes.set_xlim(0, 25)
        self.MplWidget.canvas.axes.set_ylim(0, 15)
        x_lim = self.MplWidget.canvas.axes.get_xlim()
        y_lim = self.MplWidget.canvas.axes.get_ylim()
        if coords[0] >= (x_lim[0] + np.diff(x_lim) / 2):
            x_value = -20
        else:
            x_value = 20

        if coords[1] > (y_lim[0] + np.diff(y_lim) / 2):
            y_value = -20
        else:
            y_value = 20
        return x_value, y_value

    @staticmethod
    # function to help set the horizontal alignment of the label
    def set_ha_value(xy_text):
        if xy_text[0] < 0:
            return 'right'
        else:
            return 'left'

    @staticmethod
    # function to help set the vertical alignment of the label
    def set_va_value(xy_text):
        if xy_text[1] > 0:
            return 'bottom'
        else:
            return 'top'

    # function for plotting the field objects according to their type and company
    def create_plot(self):
        self.MplWidget.canvas.axes.get_yaxis().set_visible(False)
        self.MplWidget.canvas.axes.get_xaxis().set_visible(False)

        x = []
        y = []
        color = []
        marker = []
        labels = []
        sizes = []

        self.is_checked(self.company1_checkbox, self.soldiers1_checkbox, self.apcs1_checkbox, self.commander1_checkbox)
        self.is_checked(self.company2_checkbox, self.soldiers2_checkbox, self.apcs2_checkbox, self.commander2_checkbox)
        self.is_checked(self.company3_checkbox, self.soldiers3_checkbox, self.apcs3_checkbox, self.commander3_checkbox)

        for s in self.soldiers:
            if s.company_number == 1:
                self.create_plot_by_companies(x, y, color, marker, sizes, labels, s, self.company1_checkbox,
                                              self.soldiers1_checkbox, self.apcs1_checkbox, 'cyan')
            elif s.company_number == 2:
                self.create_plot_by_companies(x, y, color, marker, sizes, labels, s, self.company2_checkbox,
                                              self.soldiers2_checkbox, self.apcs2_checkbox, 'orange')
            elif s.company_number == 3:
                self.create_plot_by_companies(x, y, color, marker, sizes, labels, s, self.company3_checkbox,
                                              self.soldiers3_checkbox, self.apcs3_checkbox, 'lime')
            else:
                continue

        for xp, yp, c, m, l, s in zip(x, y, color, marker, labels,
                                      sizes):  # zip connects together all the elements in the lists
            # that located on the same indexes
            self.MplWidget.canvas.axes.plot([xp], [yp], color=c, marker=m, markersize=s, label=l, picker=10)

        if self.enemies_checkBox.isChecked() and \
                not (self.enemies_soldiers_checkbox.isChecked() and self.launchers_checkbox.isChecked() and
                     self.lookout_points_checkbox.isChecked()):
            self.enemies_soldiers_checkbox.setChecked(True)
            self.launchers_checkbox.setChecked(True)
            self.lookout_points_checkbox.setChecked(True)

        if (self.enemies_checkBox.isChecked()) and not (self.enemies_soldiers_checkbox.isChecked() or
                                                        self.launchers_checkbox.isChecked() or
                                                        self.lookout_points_checkbox.isChecked()):
            self.enemies_checkBox.setChecked(False)

        if (not self.enemies_checkBox.isChecked()) and (self.enemies_soldiers_checkbox.isChecked() and
                                                        self.launchers_checkbox.isChecked() and
                                                        self.lookout_points_checkbox.isChecked()):
            self.enemies_checkBox.setChecked(True)

        x_enemy = []
        y_enemy = []
        marker_enemy = []
        for e in self.enemies:

            if (self.enemies_checkBox.isChecked() or self.enemies_soldiers_checkbox.isChecked()
                    or self.launchers_checkbox.isChecked() or self.lookout_points_checkbox.isChecked()):
                if e.get_type() == EnemyType.soldier.value and self.enemies_soldiers_checkbox.isChecked():
                    x_enemy.append(e.get_x())
                    y_enemy.append(e.get_y())
                    marker_enemy.append("o")

                elif e.get_type() == EnemyType.launcher.value and self.launchers_checkbox.isChecked():
                    x_enemy.append(e.get_x())
                    y_enemy.append(e.get_y())
                    marker_enemy.append("^")

                elif e.get_type() == EnemyType.lookout_point.value and self.lookout_points_checkbox.isChecked():
                    x_enemy.append(e.get_x())
                    y_enemy.append(e.get_y())
                    marker_enemy.append("s")

                for x, y, m in zip(x_enemy, y_enemy, marker_enemy):
                    self.MplWidget.canvas.axes.plot([x], [y], color="red", marker=m, markersize=4,
                                                    markeredgecolor="black")
        x_cc = []
        y_cc = []
        color_cc = []

        for c in self.company_commanders:
            if (self.company1_checkbox.isChecked() or self.commander1_checkBox.isChecked()) and c.company_number == 1:
                x_cc.append(c.x)
                y_cc.append(c.y)
                color_cc.append('cyan')

            elif (self.company2_checkbox.isChecked() or self.commander2_checkBox.isChecked()) and c.company_number == 2:
                x_cc.append(c.x)
                y_cc.append(c.y)
                color_cc.append('orange')

            elif (self.company3_checkbox.isChecked() or self.commander3_checkBox.isChecked()) and c.company_number == 3:
                x_cc.append(c.x)
                y_cc.append(c.y)
                color_cc.append('lime')

            else:
                continue

            for xcc, ycc, co in zip(x_cc, y_cc, color_cc):
                self.MplWidget.canvas.axes.plot([xcc], [ycc], color="black",  marker='o', markersize=7, picker=10,
                                                markeredgecolor=co, markeredgewidth=1.5)

    @staticmethod
    def create_plot_by_companies(x, y, color, marker, sizes, labels, s, company, soldiers, apcs, c):
        if company.isChecked() or soldiers.isChecked() or apcs.isChecked():
            if type(s) == Soldier and soldiers.isChecked():
                x.append(s.x)
                y.append(s.y)
                color.append(c)
                marker.append('o')
                sizes.append(4)
                labels.append(s.__str__())

            elif type(s) == APC and apcs.isChecked():
                x.append(s.x)
                y.append(s.y)
                color.append(c)
                marker.append('*')
                sizes.append(8)
                labels.append(s.__str__())

    @staticmethod
    def is_checked(company, soldiers, apcs, commander):
        if company.isChecked() and not (soldiers.isChecked() and
                                        apcs.isChecked() and commander.isChecked()):
            soldiers.setChecked(True)
            apcs.setChecked(True)
            commander.setChecked(True)

        if (company.isChecked()) and not (soldiers.isChecked() or
                                          apcs.isChecked() or commander.isChecked()):
            company.setChecked(False)

        if (not company.isChecked()) and (soldiers.isChecked()
                                          and apcs.isChecked() and commander.isChecked()):
            company.setChecked(True)

    @staticmethod
    def get_color(company_num):
        if company_num == 1:
            return "cyan"
        elif company_num == 2:
            return "orange"
        else:
            return "lime"

            # returns the soldier's company according to the location

    def get_company_num(self, x_data, y_data):
        for soldier in self.soldiers:
            if soldier.x == x_data and soldier.y == y_data:
                return soldier.company_number

    # function for handling the hover event for showing labels for markers
    def on_hover(self, event):
        if event.inaxes == self.MplWidget.canvas.axes:  # event.inaxes = the axes that the event occurs in
            # self.canves.ax = our axes

            for line in self.MplWidget.canvas.axes.lines:  # all the markers we plotted
                contains, index = line.contains(event)  # is the artist contains the picked point
                if contains:
                    self.tooltip.set_text(line.get_label())  # sets the right label for the point
                    self.tooltip.set_x(line.get_xdata())
                    self.tooltip.set_y(line.get_ydata())
                    self.tooltip.set_visible(True)
                    self.tooltip_coords = line.get_xdata(), line.get_ydata()
                    self.tooltip_text = line.get_label()
                    break
                else:
                    self.tooltip.set_visible(False)
        self.tooltip_visible = self.tooltip._visible
        # redraw the canvas to display or hide the label
        self.MplWidget.canvas.draw()


def battalion_commander_thread():
    BattalionCommander.main()


def gui_thread():
    app = QApplication(sys.argv)
    window = MatplotlibWidget()
    window.show()
    update_field_thread = threading.Thread(target=window.update_field)
    update_field_thread.start()
    sys.exit(app.exec_())


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    bc_thread = threading.Thread(target=battalion_commander_thread)
    gui_thread2 = threading.Thread(target=gui_thread)

    bc_thread.start()
    gui_thread2.start()

main()
