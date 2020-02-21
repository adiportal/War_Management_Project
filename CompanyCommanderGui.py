import sys
import threading
import time
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import Entities
import Utility
from Entities import Soldier, APC, Packet
import numpy as np
import CompanyCommanderUDP
from CompanyCommanderUDP import send_handler
from Utility import EnemyType, Sender, Receiver, MessageType


class MatplotlibWidget(QMainWindow):
    soldiers = []  # company1 list from the 3 lists of the company commander
    picked_soldier = []
    picked_enemy = []
    enemies = []
    company_commander = CompanyCommanderUDP.company_commander  # Initialize the company commander entity
    console_messages = CompanyCommanderUDP.console_messages
    soldier_was_picked = False
    enemy_was_picked = False

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi("company_commander3.ui", self)

        self.move_pushButton.clicked.connect(self.move_button)
        self.engage_pushButton.clicked.connect(self.engage_button)
        self.cancelButton.clicked.connect(self.cancel_button)
        self.cancelButton.setToolTip("Cancel the chosen soldiers")
        self.console.setReadOnly(True)
        self.cursor = QTextCursor(self.console.document())

        self.setWindowTitle("Company Commander " + str(CompanyCommanderUDP.company_commander.company_number))

        self.tooltip_visible = False
        self.tooltip_coords = 0, 0
        self.tooltip_text = ''
        self.my_company_checkbox = self.treeFilter.topLevelItem(0)
        self.soldiers_checkbox = self.treeFilter.topLevelItem(0).child(0)
        self.apcs_checkbox = self.treeFilter.topLevelItem(0).child(1)
        self.other_companies_checkbox = self.treeFilter.topLevelItem(1)
        self.enemies_checkbox = self.treeFilter.topLevelItem(2)
        self.enemies_soldiers_checkbox = self.treeFilter.topLevelItem(2).child(0)
        self.launchers_checkbox = self.treeFilter.topLevelItem(2).child(1)
        self.lookout_points_checkbox = self.treeFilter.topLevelItem(2).child(2)

        # Starting the animation using the animate function, update every 1000 miliseconds
        self.ani = FuncAnimation(self.MplWidget.canvas.figure, self.animate, interval=1000, blit=False)

        # Starting the hover event (on hovering a marker an informative label shows up)
        self.MplWidget.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.MplWidget.canvas.mpl_connect("pick_event", self.on_pick)

        # self.my_company_checkbox.setChecked(True)
        # self.other_companies_checkbox.setChecked(True)
        # self.enemies_checkBox.setChecked(True)

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
        self.move_pushButton.setDown(True)
        self.MplWidget.canvas.mpl_connect('button_press_event', self.on_click)

    # function for a thread, updates the soldiers list
    def update_field(self):
        while True:
            self.soldiers = CompanyCommanderUDP.company1 + CompanyCommanderUDP.company2 + CompanyCommanderUDP.company3
            self.enemies = CompanyCommanderUDP.company_commander.get_enemies()
            self.console_messages_thread()
            time.sleep(2.0)

        # function for the FuncAnimation option, clears and create the plot again

    def console_messages_thread(self):
        # red_color = QColor(255, 0, 0)
        # black_color = QColor(0, 0, 0)
        if len(self.console_messages) > 0:
            current = self.console_messages.pop()
            if current[1] == Utility.MessageType.got_shot.value:
                red_text = "<span style=\" font-size:8pt; font-weight:400; color:#ff0000;\" >"
                red_text += (current[0])
                red_text += "</span>"
                self.cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor, 1)
                self.console.setTextCursor(self.cursor)
                self.console.insertHtml(red_text)

            else:
                black_text = "<span style=\" font-size:8pt; font-weight:400; color:#000000;\" >"
                black_text += (current[0])
                black_text += "</span>"
                self.cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor, 1)
                self.console.setTextCursor(self.cursor)
                self.console.insertHtml(black_text)

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

        # Conditions for checkboxes

        # My Company Part
        # my company - checked, soldiers + apcs not
        if self.my_company_checkbox.checkState(0) == QtCore.Qt.Checked and (
                self.soldiers_checkbox.checkState(0) == QtCore.Qt.Unchecked and
                self.apcs_checkbox.checkState(0) == QtCore.Qt.Unchecked):
            self.soldiers_checkbox.setCheckState(0, QtCore.Qt.Checked)
            self.apcs_checkbox.setCheckState(0, QtCore.Qt.Checked)

        # my company - unchecked, soldiers - checked, apcs - unchecked
        if (self.my_company_checkbox.checkState(0) == QtCore.Qt.Unchecked or
            self.my_company_checkbox.checkState(0) == QtCore.Qt.Checked) and (
                self.soldiers_checkbox.checkState(0) == QtCore.Qt.Checked and
                self.apcs_checkbox.checkState(0) == QtCore.Qt.Unchecked):
            self.my_company_checkbox.setCheckState(0, QtCore.Qt.PartiallyChecked)

        # my company - unchecked, soldiers - unchecked, apcs - checked
        if (self.my_company_checkbox.checkState(0) == QtCore.Qt.Unchecked or
            self.my_company_checkbox.checkState(0) == QtCore.Qt.Checked) and (
                self.soldiers_checkbox.checkState(0) == QtCore.Qt.Unchecked and
                self.apcs_checkbox.checkState(0) == QtCore.Qt.Checked):
            self.my_company_checkbox.setCheckState(0, QtCore.Qt.PartiallyChecked)

        # my company - unchecked, soldiers - checked, apcs - checked
        if self.my_company_checkbox.checkState(0) == QtCore.Qt.Unchecked and (
                self.soldiers_checkbox.checkState(0) == QtCore.Qt.Checked
                and self.apcs_checkbox.checkState(0) == QtCore.Qt.Checked):
            self.soldiers_checkbox.setCheckState(0, QtCore.Qt.Unchecked)
            self.apcs_checkbox.setCheckState(0, QtCore.Qt.Unchecked)

        # my company - partially checked, soldiers - checked, apcs - checked
        if self.my_company_checkbox.checkState(0) == QtCore.Qt.PartiallyChecked and (
                self.soldiers_checkbox.checkState(0) == QtCore.Qt.Checked and
                self.apcs_checkbox.checkState(0) == QtCore.Qt.Checked):
            self.my_company_checkbox.setCheckState(0, QtCore.Qt.Checked)

        # my company - partially checked, soldiers - unchecked, apcs - unchecked
        if self.my_company_checkbox.checkState(0) == QtCore.Qt.PartiallyChecked and (
                self.soldiers_checkbox.checkState(0) == QtCore.Qt.Unchecked and
                self.apcs_checkbox.checkState(0) == QtCore.Qt.Unchecked):
            self.my_company_checkbox.setCheckState(0, QtCore.Qt.Unchecked)

        for s in self.soldiers:
            if self.my_company_checkbox.checkState(0) == QtCore.Qt.Checked or self.soldiers_checkbox.checkState(
                    0) == QtCore.Qt.Checked or \
                    self.apcs_checkbox.checkState(0) == QtCore.Qt.Checked:
                if type(s) == Soldier and self.soldiers_checkbox.checkState(0) == QtCore.Qt.Checked:
                    if s.company_number == self.company_commander.company_number:
                        x.append(s.x)
                        y.append(s.y)
                        if self.picked_soldier.__contains__(s):
                            color.append('yellow')

                        elif s.company_number == 1:
                            color.append('cyan')
                        elif s.company_number == 2:
                            color.append('orange')
                        else:
                            color.append('lime')
                        marker.append('o')
                        sizes.append(4)
                        labels.append(s.__str__())

                elif type(s) == APC and self.apcs_checkbox.checkState(0) == QtCore.Qt.Checked:
                    if s.company_number == self.company_commander.company_number:
                        x.append(s.x)
                        y.append(s.y)
                        if s in self.picked_soldier:
                            color.append('yellow')
                        else:
                            if s.company_number == 1:
                                color.append('cyan')
                            elif s.company_number == 2:
                                color.append('orange')
                            else:
                                color.append('lime')

                        marker.append('*')
                        sizes.append(8)
                        labels.append(s.__str__())

            if self.other_companies_checkbox.checkState(0) == QtCore.Qt.Checked:
                if s.company_number != self.company_commander.company_number:
                    x.append(s.x)
                    y.append(s.y)
                    if s.company_number == 1 and self.company_commander.company_number != 1:
                        color.append('cyan')
                    elif s.company_number == 2 and self.company_commander.company_number != 2:
                        color.append('orange')
                    elif s.company_number == 3 and self.company_commander.company_number != 3:
                        color.append('lime')
                    if type(s) == Soldier:
                        marker.append('o')
                        sizes.append(4)
                    else:
                        marker.append('*')
                        sizes.append(8)
                    labels.append(s.__str__())
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

        x_enemy = []
        y_enemy = []
        marker_enemy = []
        for e in self.enemies:

            if (self.enemies_checkbox.checkState(0) == QtCore.Qt.Checked or self.enemies_soldiers_checkbox.checkState(
                    0) == QtCore.Qt.Checked
                    or self.launchers_checkbox.checkState(0) == QtCore.Qt.Checked or
                    self.lookout_points_checkbox.checkState(0) == QtCore.Qt.Checked):
                if e.get_type() == EnemyType.soldier.value and self.enemies_soldiers_checkbox.checkState(0) == QtCore.Qt.Checked:
                    x_enemy.append(e.get_x())
                    y_enemy.append(e.get_y())
                    marker_enemy.append("o")

                elif e.get_type() == EnemyType.launcher.value and \
                        self.launchers_checkbox.checkState(0) == QtCore.Qt.Checked:
                    x_enemy.append(e.get_x())
                    y_enemy.append(e.get_y())
                    marker_enemy.append("^")

                elif e.get_type() == EnemyType.lookout_point.value and self.lookout_points_checkbox.checkState(
                        0) == QtCore.Qt.Checked:
                    x_enemy.append(e.get_x())
                    y_enemy.append(e.get_y())
                    marker_enemy.append("s")

                for x, y, m in zip(x_enemy, y_enemy, marker_enemy):
                    self.MplWidget.canvas.axes.plot([x], [y], color="red", marker=m, markersize=7,
                                                    markeredgecolor="black")

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

    # # function for handling the pick event when picking a marker to move
    # def on_pick(self, event):
    #     # QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))
    #     this_point = event.artist
    #
    #     # x_data and y_data of the point that was picked by the user
    #     x_data = this_point.get_xdata()
    #     y_data = this_point.get_ydata()
    #
    #     ind = event.ind
    #
    #     if self.company_commander.company_number == self.get_company_num(x_data, y_data):
    #
    #         for soldier in self.soldiers:
    #             if soldier.x == x_data and soldier.y == y_data:
    #                 self.picked_soldier.append(soldier)
    #                 break
    #
    #         # turns on the on click event
    #         self.cursor.insertText("Please pick a point you want to move to\n")
    #         self.cursor.movePosition(QTextCursor.End)
    #         self.MplWidget.canvas.mpl_connect('button_press_event', self.on_click)
    #         # turns off the on pick event (so only click on point to move is able)
    #         self.MplWidget.canvas.mpl_disconnect(self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick))

    # def pick_soldier_for_engage(self, event):
    #     if len(self.picked_soldier) > 0:
    #         self.picked_soldier.pop(0)
    #     this_point = event.artist
    #
    #     # x_data and y_data of the point that was picked by the user
    #     x_data = this_point.get_xdata()
    #     y_data = this_point.get_ydata()
    #
    #     ind = event.ind
    #
    #     if self.company_commander.company_number == self.get_company_num(x_data, y_data):
    #         for soldier in self.soldiers:
    #             if soldier.x == x_data and soldier.y == y_data:
    #                 self.picked_soldier.append(soldier)
    #                 break
    #         self.MplWidget.canvas.mpl_disconnect(
    #             self.MplWidget.canvas.mpl_connect('pick_event', self.pick_soldier_for_engage))
    #         # self.MplWidget.canvas.mpl_connect('pick_event', self.pick_enemy_for_engage)
    #         print("pick soldier completed")
    #         self.soldier_was_picked = True
    #         self.cursor.insertText("soldier was picked\n")
    #
    # def pick_enemy_for_engage(self, event):
    #     if len(self.picked_enemy) > 0:
    #         self.picked_enemy.pop(0)
    #     point = event.artist
    #
    #     # x_data and y_data of the point that was picked by the user
    #     x_data = point.get_xdata()
    #     y_data = point.get_ydata()
    #
    #     ind = event.ind
    #
    #     for enemy in self.enemies:
    #         if enemy.x == x_data and enemy.y == y_data:
    #             self.picked_enemy.append(enemy)
    #             break
    #     self.MplWidget.canvas.mpl_disconnect(self.MplWidget.canvas.mpl_connect('pick_event',
    #                                                                            self.pick_enemy_for_engage))
    #     print("pick enemy completed")
    #     self.cursor.insertText("enemy was picked\n")
    #
    #     if len(self.picked_enemy) > 0 and len(self.picked_soldier) > 0:
    #         soldier = self.picked_soldier[0]
    #         enemy = self.picked_enemy[0]
    #
    #         message = Entities.EngageOrderMessage(soldier, enemy)
    #
    #         packet = Packet(Sender.company_commander.value, self.company_commander.company_number,
    #                         Receiver.soldier.value,
    #                         MessageType.engage_order.value, message)
    #         send_handler(packet)
    #         print("message sent")

    # def engage(self):
    #     soldier = self.picked_soldier[0]
    #     enemy = self.picked_enemy[0]
    #     message = Entities.EngageOrderMessage(soldier, enemy)
    #
    #     packet = Packet(Sender.company_commander.value, self.company_commander.company_number, Receiver.soldier.value,
    #                     MessageType.engage_order.value, message)
    #     send_handler(packet)
    #     print("message sent")

    def cancel_button(self):
        self.picked_soldier.clear()
        self.move_pushButton.setEnabled(False)
        self.engage_pushButton.setEnabled(False)
        self.cancelButton.setEnabled(False)
        if self.move_pushButton.isDown():
            self.MplWidget.canvas.mpl_disconnect(
                self.MplWidget.canvas.mpl_connect('button_press_event', self.on_click))
        elif self.engage_pushButton.isDown():
            self.MplWidget.canvas.mpl_connect("pick_event", self.on_pick)
            self.MplWidget.canvas.mpl_disconnect(self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick_enemy))
        else:
            pass

    def engage_button(self):
        self.engage_pushButton.setDown(True)
        self.MplWidget.canvas.mpl_disconnect(self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick))
        self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick_enemy)

    # returns the soldier's company according to the location
    def get_company_num(self, x_data, y_data):
        for soldier in self.soldiers:
            if soldier.x == x_data and soldier.y == y_data:
                return soldier.company_number

    # # function for handling the click event for choosing a new location
    def on_click(self, event):
        # x and y values that was chosen
        x_data = event.xdata
        y_data = event.ydata
        if len(self.picked_soldier) > 0:  # means that a field object actually was chosen

            # Send move message for the chosen field object with UDP
            for soldier in self.picked_soldier:
                packet = Utility.create_move_to_message(soldier.get_company_num(), soldier.get_id(), (x_data, y_data))
                CompanyCommanderUDP.send_handler(packet)
                time.sleep(0.1)

        self.picked_soldier.clear()
        self.move_pushButton.setEnabled(False)
        self.engage_pushButton.setEnabled(False)
        self.cancelButton.setEnabled(False)


        # turns off the click event
        self.MplWidget.canvas.mpl_disconnect(
            self.MplWidget.canvas.mpl_connect('button_press_event', self.on_click))

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

    def on_pick(self, event):
        this_point = event.artist

        # x_data and y_data of the point that was picked by the user
        x_data = this_point.get_xdata()
        y_data = this_point.get_ydata()

        if self.company_commander.company_number == self.get_company_num(x_data, y_data):

            for soldier in self.soldiers:
                if soldier.x == x_data and soldier.y == y_data and soldier not in self.picked_soldier:
                    self.picked_soldier.append(soldier)
                    self.move_pushButton.setEnabled(True)
                    self.engage_pushButton.setEnabled(True)
                    self.cancelButton.setEnabled(True)
                    break
        print(x_data, y_data)
        print(self.picked_soldier)

    def on_pick_enemy(self, event):
        this_point = event.artist

        # x_data and y_data of the point that was picked by the user
        x_data = this_point.get_xdata()
        y_data = this_point.get_ydata()

        for enemy in self.enemies:
            if enemy.x == x_data and enemy.y == y_data:
                self.picked_enemy.append(enemy)
                break
        print(x_data, y_data)
        print(self.picked_enemy.__str__())

        self.engage_pushButton.setDown(False)

        for soldier in self.picked_soldier:
            message = Entities.EngageOrderMessage(soldier, enemy)
            packet = Packet(Sender.company_commander.value, self.company_commander.company_number, Receiver.soldier.value,
                            MessageType.engage_order.value, message)
            send_handler(packet)
            print("message sent")
            time.sleep(0.1)

        self.picked_soldier.clear()
        self.picked_enemy.clear()
        self.move_pushButton.setEnabled(False)
        self.engage_pushButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

        self.MplWidget.canvas.mpl_connect("pick_event", self.on_pick)
        self.MplWidget.canvas.mpl_disconnect(self.MplWidget.canvas.mpl_connect('pick_event', self.on_pick_enemy))


def company_commander_thread(company_num, location):
    CompanyCommanderUDP.main(company_num, location)


def gui_thread():
    app = QApplication(sys.argv)
    window = MatplotlibWidget()
    window.show()
    update_field_thread = threading.Thread(target=window.update_field)
    # console_thread = threading.Thread(target=window.console_messages_thread)
    update_field_thread.start()
    # console_thread.start()
    sys.exit(app.exec_())


def main(company_num, location):
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    cc_thread = threading.Thread(target=company_commander_thread, args=(company_num, location))
    gui_thread1 = threading.Thread(target=gui_thread)

    cc_thread.start()
    gui_thread1.start()


main(1, (1, 2))
