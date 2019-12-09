import sys
import threading
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from Entities import Soldier
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import numpy as np
import CompanyCommanderUDP
from CompanyCommanderUDP import send_handler
from Utility import create_move_to_message, EnemyType


class MatplotlibWidget(QMainWindow):
    soldiers = []  # company1 list from the 3 lists of the company commander
    picked_soldier = []
    enemies = []

    company_commander = CompanyCommanderUDP.company_commander  # Initialize the company commander entity

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi("company_commander1.ui", self)

        self.move_pushButton.clicked.connect(self.move_button)

        self.setWindowTitle("Company Commander " + str(CompanyCommanderUDP.company_commander.company_number))

        self.tooltip_visible = False
        self.tooltip_coords = 0, 0
        self.tooltip_text = ''

        # Starting the animation using the animate function, update every 1000 miliseconds
        self.ani = FuncAnimation(self.MplWidget.canvas.figure, self.animate, interval=1000, blit=False)

        # Starting the pick event (first you pick an existing point and after that a new location)
        # self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick)

        # Starting the hover event (on hovering a marker an informative label shows up)
        self.MplWidget.canvas.mpl_connect("motion_notify_event", self.on_hover)

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

    def move_button(self):
        self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick)
        self.messages_label.setText("Please choose Soldier or BTW")

    # function for a thread, updates the soldiers list
    def update_field(self):
        while True:
            self.soldiers = CompanyCommanderUDP.company1 + CompanyCommanderUDP.company2 + CompanyCommanderUDP.company3
            self.enemies = CompanyCommanderUDP.company_commander.get_enemies()
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

        for s in self.soldiers:
            x.append(s.x)
            y.append(s.y)
            if s.company_number == 1:
                color.append('cyan')
            elif s.company_number == 2:
                color.append('orange')
            else:
                color.append('lime')
            if type(s) == Soldier:
                marker.append('o')
                sizes.append(4)
            else:
                marker.append('*')
                sizes.append(8)
            labels.append(s.__str__())

        for xp, yp, c, m, l, s in zip(x, y, color, marker, labels,
                                      sizes):  # zip connects together all the elements in the lists
            # that located on the same indexes
            self.MplWidget.canvas.axes.plot([xp], [yp], color=c, marker=m, markersize=s, label=l, picker=10)

        x_enemy = []
        y_enemy = []
        marker_enemy = []
        for e in self.enemies:
            x_enemy.append(e.get_x())
            y_enemy.append(e.get_y())

            if e.get_type() == EnemyType.soldier.value:
                marker_enemy.append("o")

            elif e.get_type() == EnemyType.launcher:
                marker_enemy.append("^")

            else:
                marker_enemy.append("s")

            for x, y, m in zip(x_enemy, y_enemy, marker_enemy):
                self.MplWidget.canvas.axes.plot([x], [y], color="red", marker=m, markersize=4, markeredgecolor="black")

        # Plot the company commander location
        self.MplWidget.canvas.axes.plot(self.company_commander.x, self.company_commander.y, color="black", marker='o',
                                        markersize=7, label=self.company_commander.__str__(),
                                        picker=10,
                                        markeredgecolor=self.get_color(self.company_commander.company_number),
                                        markeredgewidth=1.5)

    @staticmethod
    def get_color(company_num):
        if company_num == 1:
            return "cyan"
        elif company_num == 2:
            return "orange"
        else:
            return "lime"

    # function for handling the pick event when picking a marker to move
    def on_pick(self, event):
        this_point = event.artist

        # x_data and y_data of the point that was picked by the user
        x_data = this_point.get_xdata()
        y_data = this_point.get_ydata()

        ind = event.ind

        if self.company_commander.company_number == self.get_company_num(x_data, y_data):

            for soldier in self.soldiers:
                if soldier.x == x_data and soldier.y == y_data:
                    index = soldier.ID - 1
                    self.picked_soldier.append(soldier)
                    break

            # turns on the on click event
            self.MplWidget.canvas.mpl_connect('button_press_event', self.on_click)
            # turns off the on pick event (so only click on point to move is able)
            self.MplWidget.canvas.mpl_disconnect(self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick))

    # returns the soldier's company according to the location
    def get_company_num(self, x_data, y_data):
        for soldier in self.soldiers:
            if soldier.x == x_data and soldier.y == y_data:
                return soldier.company_number

    # function for handling the click event for choosing a new location
    def on_click(self, event):
        # x and y values that was chosen
        x_data = event.xdata
        y_data = event.ydata
        if len(self.picked_soldier) > 0:  # means that a field object actually was chosen

            soldier = self.picked_soldier.pop(0)  # empty the list for the next field object

            # Send move message for the chosen field object with UDP
            packet = create_move_to_message(soldier.get_company_num(), soldier.get_id(), (x_data, y_data))
            send_handler(packet)

        self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick)  # turns on again the pick event
        # turns off the click event
        self.MplWidget.canvas.mpl_disconnect(
            self.MplWidget.canvas.mpl_connect('button_press_event', self.on_click))

        self.messages_label.setText("")


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

                    # check if the current company commander is the cc of the picked field object
                    if self.company_commander.company_number == self.get_company_num(line.get_xdata(),
                                                                                     line.get_ydata()):
                        self.tooltip.set_visible(True)
                        self.tooltip_coords = line.get_xdata(), line.get_ydata()
                        self.tooltip_text = line.get_label()
                        break
            else:
                self.tooltip.set_visible(False)
        self.tooltip_visible = self.tooltip._visible
        # redraw the canvas to display or hide the label
        self.MplWidget.canvas.draw()

    # def update_graph(self):
    #
    #     self.MplWidget.canvas.axes.plot([1], [2], color="red", marker='*', markersize=6)
    #
    #     self.MplWidget.canvas.draw()


def company_commander_thread(company_num, location):
    CompanyCommanderUDP.main(company_num, location)


def gui_thread():
    app = QApplication(sys.argv)
    window = MatplotlibWidget()
    window.show()
    update_field_thread = threading.Thread(target=window.update_field)
    update_field_thread.start()
    sys.exit(app.exec_())


def main(company_num, location):
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    cc_thread = threading.Thread(target=company_commander_thread, args=(company_num, location))
    gui_thread1 = threading.Thread(target=gui_thread)

    cc_thread.start()
    gui_thread1.start()


main(1, (1, 2))
