import sys
import threading
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import CompanyCommanderUDP
from CompanyCommanderUDP import send_handler
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from Entities import Soldier, CompanyCommander
from Utility import create_move_to_message


# Class for creating matplotlib canvas (where the plot is going to be located)
class MyMplCanvas(FigureCanvas):
    fig = Figure(figsize=(10, 12), dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    def __init__(self, parent=None):
        FigureCanvas.__init__(self, MyMplCanvas.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


# The whole window of the application with all the elements
class ApplicationWindow(QtWidgets.QMainWindow):
    soldiers = []  # company1 list from the 3 lists of the company commander
    picked_soldier = []

    company_commander = CompanyCommanderUDP.company_commander  # Initialize the company commander entity

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.main_widget = QtWidgets.QWidget(self)

        vbox = QtWidgets.QVBoxLayout(self.main_widget)

        self.canvas = MyMplCanvas(self.main_widget)  # canvas calls for the matplotlib canvas

        vbox.addWidget(self.canvas)

        self.setLayout(vbox)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.tooltip_visible = False
        self.tooltip_coords = 0, 0
        self.tooltip_text = ''

        # Starting the animation using the animate function, update every 1000 miliseconds
        self.ani = FuncAnimation(self.canvas.figure, self.animate, interval=1000, blit=False)

        # Starting the pick event (first you pick an existing point and after that a new location)
        self.canvas.figure.canvas.mpl_connect('pick_event', self.on_pick)

        # Starting the hover event (on hovering a marker an informative label shows up)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.setWindowTitle("Company Commander " + str(CompanyCommanderUDP.company_commander.company_number))

    # function for a thread, updates the soldiers list
    def update_field(self):
        while True:
            self.soldiers = CompanyCommanderUDP.company1 + CompanyCommanderUDP.company2 + CompanyCommanderUDP.company3
            time.sleep(2.0)

    # function for the FuncAnimation option, clears and create the plot again
    def animate(self, i):
        self.canvas.ax.clear()
        img = plt.imread("MAP.png")
        self.canvas.ax.imshow(img)
        self.canvas.ax.imshow(img, extent=[0, 15, 0, 10])
        # Starting the properties of the marker's labels
        self.tooltip = self.canvas.ax.annotate(self.tooltip_text, self.tooltip_coords,
                                               xytext=self.set_xy_text(self.tooltip_coords),
                                               textcoords="offset points",
                                               ha=self.set_ha_value(self.set_xy_text(self.tooltip_coords)),
                                               va=self.set_va_value(self.set_xy_text(self.tooltip_coords)),
                                               size=6, bbox=dict(facecolor='wheat', boxstyle="round", alpha=0.8),
                                               arrowprops=dict(shrink=15, facecolor='black', width=3, headlength=8))
        self.tooltip.set_visible(self.tooltip_visible)  # Set the visibility of the label according to its current mode
        self.create_plot()

    def set_xy_text(self, coords):  # function to help set the position of the text in the label according to the
                                    # loccation of the marker in the plot
        self.canvas.ax.set_xlim(0, 14)
        self.canvas.ax.set_ylim(0, 10)
        x_lim = self.canvas.ax.get_xlim()
        y_lim = self.canvas.ax.get_ylim()
        if coords[0] >= (x_lim[0] + np.diff(x_lim)/2):
            x_value = -20
        else:
            x_value = 20

        if coords[1] > (y_lim[0] + np.diff(y_lim)/2):
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
        self.canvas.ax.get_yaxis().set_visible(False)
        self.canvas.ax.get_xaxis().set_visible(False)

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
                color.append('blue')
            elif s.company_number == 2:
                color.append('orange')
            else:
                color.append('green')
            if type(s) == Soldier:
                marker.append('o')
                sizes.append(4)
            else:
                marker.append('*')
                sizes.append(8)
            labels.append(s.__str__())

        for xp, yp, c, m, l, s in zip(x, y, color, marker, labels, sizes):  # zip connects together all the elements in the lists
                                                                  # that located on the same indexes
            MyMplCanvas.ax.plot([xp], [yp], color=c, marker=m, markersize=s, label=l, picker=10)

        # Plot the company commander location
        MyMplCanvas.ax.plot(self.company_commander.x, self.company_commander.y, color="black", marker='o', markersize=7, label=self.company_commander.__str__(),
                            picker=10, markeredgecolor=self.get_color(self.company_commander.company_number), markeredgewidth=1.5)

    @staticmethod
    def get_color(company_num):
        if company_num == 1:
            return "blue"
        elif company_num == 2:
            return "orange"
        else:
            return "green"

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
            MyMplCanvas.fig.canvas.mpl_connect('button_press_event', self.on_click)
            # turns off the on pick event (so only click on point to move is able)
            MyMplCanvas.fig.canvas.mpl_disconnect(MyMplCanvas.fig.canvas.mpl_connect('pick_event', self.on_pick))

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

        MyMplCanvas.fig.canvas.mpl_connect('pick_event', self.on_pick)  # turns on again the pick event
        # turns off the click event
        MyMplCanvas.fig.canvas.mpl_disconnect(MyMplCanvas.fig.canvas.mpl_connect('button_press_event', self.on_click))

    # function for handling the hover event for showing labels for markers
    def on_hover(self, event):
        if event.inaxes == self.canvas.ax:  # event.inaxes = the axes that the event occurs in
                                            # self.canves.ax = our axes

            for line in self.canvas.ax.lines:  # all the markers we plotted
                contains, index = line.contains(event)  # is the artist contains the picked point
                if contains:
                    self.tooltip.set_text(line.get_label())  # sets the right label for the point
                    self.tooltip.set_x(line.get_xdata())
                    self.tooltip.set_y(line.get_ydata())

                    # check if the current company commander is the cc of the picked field object
                    if self.company_commander.company_number == self.get_company_num(line.get_xdata(), line.get_ydata()):
                        self.tooltip.set_visible(True)
                        self.tooltip_coords = line.get_xdata(), line.get_ydata()
                        self.tooltip_text = line.get_label()
                        break
            else:
                self.tooltip.set_visible(False)
        self.tooltip_visible = self.tooltip._visible
        # redraw the canvas to display or hide the label
        self.canvas.draw()


def company_commander_thread(company_num, location):
    CompanyCommanderUDP.main(company_num, location)


def gui_thread():
    App = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    update_field_thread = threading.Thread(target=aw.update_field)
    update_field_thread.start()
    sys.exit(App.exec_())


def main(company_num, location):
    cc_thread = threading.Thread(target=company_commander_thread, args=(company_num, location))
    gui_thread1 = threading.Thread(target=gui_thread)

    cc_thread.start()
    gui_thread1.start()

