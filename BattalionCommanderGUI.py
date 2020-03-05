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
import numpy as np
from Utility import EnemyType
from map_key import Ui_MainWindow


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
        self.map_key_button.clicked.connect(self.map_key_window)

        self.company1 = self.treeWidget.topLevelItem(0)
        self.company1_commander = self.treeWidget.topLevelItem(0).child(0)
        self.company1_soldiers = self.treeWidget.topLevelItem(0).child(1)
        self.company1_apcs = self.treeWidget.topLevelItem(0).child(2)
        self.company2 = self.treeWidget.topLevelItem(1)
        self.company2_commander = self.treeWidget.topLevelItem(1).child(0)
        self.company2_soldiers = self.treeWidget.topLevelItem(1).child(1)
        self.company2_apcs = self.treeWidget.topLevelItem(1).child(2)
        self.company3 = self.treeWidget.topLevelItem(2)
        self.company3_commander = self.treeWidget.topLevelItem(2).child(0)
        self.company3_soldiers = self.treeWidget.topLevelItem(2).child(1)
        self.company3_apcs = self.treeWidget.topLevelItem(2).child(2)
        self.enemies_checkbox = self.treeWidget.topLevelItem(3)
        self.enemies_soldiers_checkbox = self.treeWidget.topLevelItem(3).child(0)
        self.launchers_checkbox = self.treeWidget.topLevelItem(3).child(1)
        self.lookout_points_checkbox = self.treeWidget.topLevelItem(3).child(2)

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

    def map_key_window(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()

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

        self.is_checked(self.company1, self.company1_soldiers, self.company1_apcs, self.company1_commander)
        self.is_checked(self.company2, self.company2_soldiers, self.company2_apcs, self.company2_commander)
        self.is_checked(self.company3, self.company3_soldiers, self.company3_apcs, self.company3_commander)

        for s in self.soldiers:
            if s.company_number == 1:
                self.create_plot_by_companies(x, y, color, marker, sizes, labels, s, self.company1,
                                              self.company1_soldiers, self.company1_apcs, 'cyan')
            elif s.company_number == 2:
                self.create_plot_by_companies(x, y, color, marker, sizes, labels, s, self.company2,
                                              self.company2_soldiers, self.company2_apcs, 'orange')
            elif s.company_number == 3:
                self.create_plot_by_companies(x, y, color, marker, sizes, labels, s, self.company3,
                                              self.company3_soldiers, self.company3_apcs, 'lime')
            else:
                continue

        for xp, yp, c, m, l, s in zip(x, y, color, marker, labels,
                                      sizes):  # zip connects together all the elements in the lists
            # that located on the same indexes
            self.MplWidget.canvas.axes.plot([xp], [yp], color=c, marker=m, markersize=s, label=l, picker=10)

        # Enemies Part
        if self.enemies_checkbox.checkState(0) == QtCore.Qt.Checked and (
                self.enemies_soldiers_checkbox.checkState(0) == QtCore.Qt.Unchecked and
                self.launchers_checkbox.checkState(0) == QtCore.Qt.Unchecked and
                self.lookout_points_checkbox.checkState(0) == QtCore.Qt.Unchecked):
            self.enemies_soldiers_checkbox.setCheckState(0, QtCore.Qt.Checked)
            self.launchers_checkbox.setCheckState(0, QtCore.Qt.Checked)
            self.lookout_points_checkbox.setCheckState(0, QtCore.Qt.Checked)

        if self.enemies_checkbox.checkState(0) == QtCore.Qt.Unchecked and (
                self.enemies_soldiers_checkbox.checkState(0) == QtCore.Qt.Checked and
                self.launchers_checkbox.checkState(0) == QtCore.Qt.Checked and
                self.lookout_points_checkbox.checkState(0) == QtCore.Qt.Checked):
            self.enemies_soldiers_checkbox.setCheckState(0, QtCore.Qt.Unchecked)
            self.launchers_checkbox.setCheckState(0, QtCore.Qt.Unchecked)
            self.lookout_points_checkbox.setCheckState(0, QtCore.Qt.Unchecked)

        if (self.enemies_checkbox.checkState(0) == QtCore.Qt.Unchecked or
            self.enemies_checkbox.checkState(0) == QtCore.Qt.Checked) and (
                self.enemies_soldiers_checkbox.checkState(0) == QtCore.Qt.Checked or
                self.launchers_checkbox.checkState(0) == QtCore.Qt.Checked or
                self.lookout_points_checkbox.checkState(0) == QtCore.Qt.Checked):
            self.enemies_checkbox.setCheckState(0, QtCore.Qt.PartiallyChecked)

        if self.enemies_checkbox.checkState(0) == QtCore.Qt.PartiallyChecked and (
                self.enemies_soldiers_checkbox.checkState(0) == QtCore.Qt.Checked and
                self.launchers_checkbox.checkState(0) == QtCore.Qt.Checked and
                self.lookout_points_checkbox.checkState(0) == QtCore.Qt.Checked):
            self.enemies_checkbox.setCheckState(0, QtCore.Qt.Checked)

        if self.enemies_checkbox.checkState(0) == QtCore.Qt.PartiallyChecked and (
                self.enemies_soldiers_checkbox.checkState(0) == QtCore.Qt.Unchecked and
                self.launchers_checkbox.checkState(0) == QtCore.Qt.Unchecked and
                self.lookout_points_checkbox.checkState(0) == QtCore.Qt.Unchecked):
            self.enemies_checkbox.setCheckState(0, QtCore.Qt.Unchecked)

        if self.enemies_checkbox.checkState(0) == QtCore.Qt.Checked and (
                self.enemies_soldiers_checkbox.checkState(0) == QtCore.Qt.Unchecked and
                self.launchers_checkbox.checkState(0) == QtCore.Qt.Checked and
                self.lookout_points_checkbox.checkState(0) == QtCore.Qt.Checked):
            self.enemies_soldiers_checkbox.setCheckState(0, QtCore.Qt.Checked)

        x_enemy = []
        y_enemy = []
        marker_enemy = []
        for e in self.enemies:

            if (self.enemies_checkbox.checkState(0) == QtCore.Qt.Checked or
                    self.enemies_soldiers_checkbox.checkState(0) == QtCore.Qt.Checked
                    or self.launchers_checkbox.checkState(0) == QtCore.Qt.Checked or
                    self.lookout_points_checkbox.checkState(0) == QtCore.Qt.Checked):
                if e.get_type() == EnemyType.soldier.value and self.enemies_soldiers_checkbox.checkState(
                        0) == QtCore.Qt.Checked:
                    x_enemy.append(e.get_x())
                    y_enemy.append(e.get_y())
                    marker_enemy.append("o")

                elif e.get_type() == EnemyType.launcher.value and self.launchers_checkbox.checkState(
                        0) == QtCore.Qt.Checked:
                    x_enemy.append(e.get_x())
                    y_enemy.append(e.get_y())
                    marker_enemy.append("^")

                elif e.get_type() == EnemyType.lookout_point.value and self.lookout_points_checkbox.checkState(
                        0) == QtCore.Qt.Checked:
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
            if (self.company1.checkState(0) == QtCore.Qt.Checked or
                self.company1_commander.checkState(0) == QtCore.Qt.Checked) \
                    and c.company_number == 1:
                x_cc.append(c.x)
                y_cc.append(c.y)
                color_cc.append('cyan')

            elif (self.company2.checkState(0) == QtCore.Qt.Checked
                  or self.company2_commander.checkState(0) == QtCore.Qt.Checked) \
                    and c.company_number == 2:
                x_cc.append(c.x)
                y_cc.append(c.y)
                color_cc.append('orange')

            elif (self.company3.checkState(0) == QtCore.Qt.Checked
                  or self.company3_commander.checkState(0) == QtCore.Qt.Checked) and c.company_number == 3:
                x_cc.append(c.x)
                y_cc.append(c.y)
                color_cc.append('lime')

            else:
                continue

            for xcc, ycc, co in zip(x_cc, y_cc, color_cc):
                self.MplWidget.canvas.axes.plot([xcc], [ycc], color="black", marker='o', markersize=7, picker=10,
                                                markeredgecolor=co, markeredgewidth=1.5)

    @staticmethod
    def create_plot_by_companies(x, y, color, marker, sizes, labels, s, company, soldiers, apcs, c):
        if company.checkState(0) == QtCore.Qt.Checked \
                or soldiers.checkState(0) == QtCore.Qt.Checked \
                or apcs.checkState(0) == QtCore.Qt.Checked:
            if type(s) == Soldier and soldiers.checkState(0) == QtCore.Qt.Checked:
                x.append(s.x)
                y.append(s.y)
                color.append(c)
                marker.append('o')
                sizes.append(4)
                labels.append(s.__str__())

            elif type(s) == APC and apcs.checkState(0) == QtCore.Qt.Checked:
                x.append(s.x)
                y.append(s.y)
                color.append(c)
                marker.append('*')
                sizes.append(8)
                labels.append(s.__str__())

    @staticmethod
    def is_checked(company, soldiers, apcs, commander):
        if company.checkState(0) == QtCore.Qt.Checked and (
                soldiers.checkState(0) == QtCore.Qt.Unchecked and
                apcs.checkState(0) == QtCore.Qt.Unchecked and
                commander.checkState(0) == QtCore.Qt.Unchecked):
            soldiers.setCheckState(0, QtCore.Qt.Checked)
            apcs.setCheckState(0, QtCore.Qt.Checked)
            commander.setCheckState(0, QtCore.Qt.Checked)

        if company.checkState(0) == QtCore.Qt.Unchecked and (
                soldiers.checkState(0) == QtCore.Qt.Checked and
                apcs.checkState(0) == QtCore.Qt.Checked and
                commander.checkState(0) == QtCore.Qt.Checked):
            soldiers.setCheckState(0, QtCore.Qt.Unchecked)
            apcs.setCheckState(0, QtCore.Qt.Unchecked)
            commander.setCheckState(0, QtCore.Qt.Unchecked)

        if (company.checkState(0) == QtCore.Qt.Unchecked or
            company.checkState(0) == QtCore.Qt.Checked) and (
                soldiers.checkState(0) == QtCore.Qt.Checked or
                apcs.checkState(0) == QtCore.Qt.Checked or
                commander.checkState(0) == QtCore.Qt.Checked):
            company.setCheckState(0, QtCore.Qt.PartiallyChecked)

        if company.checkState(0) == QtCore.Qt.PartiallyChecked and (
                soldiers.checkState(0) == QtCore.Qt.Checked and
                apcs.checkState(0) == QtCore.Qt.Checked and
                commander.checkState(0) == QtCore.Qt.Checked):
            company.setCheckState(0, QtCore.Qt.Checked)

        if company.checkState(0) == QtCore.Qt.PartiallyChecked and (
                soldiers.checkState(0) == QtCore.Qt.Unchecked and
                apcs.checkState(0) == QtCore.Qt.Unchecked and
                commander.checkState(0) == QtCore.Qt.Unchecked):
            company.setCheckState(0, QtCore.Qt.Unchecked)

        if company.checkState(0) == QtCore.Qt.Checked and (
                soldiers.checkState(0) == QtCore.Qt.Unchecked and
                apcs.checkState(0) == QtCore.Qt.Checked and
                commander.checkState(0) == QtCore.Qt.Checked):
            company.setCheckState(0, QtCore.Qt.Checked)

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
