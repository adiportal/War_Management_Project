import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, \
    QTextBrowser, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from Entities import Soldier, CompanyCommander, BTW, FieldObjects


class MyMplCanvas(FigureCanvas):
    fig = Figure(figsize=(10, 12), dpi=200)
    ax = fig.add_subplot(1, 1, 1)

    def __init__(self, parent=None):

        FigureCanvas.__init__(self, MyMplCanvas.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class ApplicationWindow(QtWidgets.QMainWindow):
    soldiers = []
    picked_soldier = []

    s1 = Soldier(1, (3, 4), 100)
    s2 = Soldier(2, (5, 6), 100)
    s3 = Soldier(3, (1, 6), 100)
    s4 = BTW(1, (2, 3), 100)
    s5 = BTW(2, (3, 3.5), 100)
    s6 = BTW(3, (4.2, 3.7), 100)
    s7 = Soldier(1, (5.3, 4), 100)
    s8 = Soldier(2, (2.6, 4.3), 100)
    s9 = Soldier(3, (7, 5.2), 100)

    c1 = CompanyCommander(2, (2, 4), 100)

    soldiers = [s1, s2, s3, s4, s5, s6, s7, s8, s9]

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Main Window")
        self.main_widget = QtWidgets.QWidget(self)

        vbox = QtWidgets.QVBoxLayout(self.main_widget)

        self.canvas = MyMplCanvas(self.main_widget)  ###attention###
        vbox.addWidget(self.canvas)


        self.setLayout(vbox)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.tooltip_visible = False
        self.tooltip_coords = 0, 0
        self.tooltip_text = ''

        self.ani = FuncAnimation(self.canvas.figure, self.animate, interval=100, blit=False)
        self.canvas.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def animate(self, i):
        self.canvas.ax.clear()
        self.tooltip = self.canvas.ax.annotate(self.tooltip_text, self.tooltip_coords,
                                               xytext=self.set_xy_text(self.tooltip_coords),
                                               textcoords="offset points",
                                               ha=self.set_ha_value(self.set_xy_text(self.tooltip_coords)),
                                               va=self.set_va_value(self.set_xy_text(self.tooltip_coords)),
                                               size=6, bbox=dict(facecolor='yellow', boxstyle="round", alpha=0.8),
                                               arrowprops=dict(shrink=15, facecolor='black', width=3, headlength=8))
        self.tooltip.set_visible(self.tooltip_visible)
        self.create_plot()

    def set_xy_text(self, coords):
        self.canvas.ax.set_xlim(0, 10)
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
    def set_ha_value(xy_text):
        if xy_text[0] < 0:
            return 'right'
        else:
            return 'left'

    @staticmethod
    def set_va_value(xy_text):
        if xy_text[1] > 0:
            return 'bottom'
        else:
            return 'top'

    def create_plot(self):
        x = []
        y = []
        color = []
        marker = []
        labels = []
        for s in self.soldiers:
            x.append(s.x)
            y.append(s.y)
            if s.company_number == 1:
                color.append('blue')
            elif s.company_number == 2:
                color.append('red')
            else:
                color.append('green')
            if type(s) == Soldier:
                marker.append('o')
            else:
                marker.append('*')
            labels.append(s.__str__())

        for xp, yp, c, m, l in zip(x, y, color, marker, labels):
            MyMplCanvas.ax.plot([xp], [yp], color=c, marker=m, markersize=5, label=l, picker=10)

    def on_pick(self, event):
        this_point = event.artist
        x_data = this_point.get_xdata()
        y_data = this_point.get_ydata()
        ind = event.ind

        if self.c1.company_number == self.get_company_num(x_data, y_data):

            for soldier in self.soldiers:
                if soldier.x == x_data and soldier.y == y_data:
                    index = soldier.ID - 1
                    self.picked_soldier.append(soldier)
                    break

            print(str(float(x_data[ind])) + ", " + str(float(y_data[ind])))
            print(str(ApplicationWindow.soldiers[index].__str__()))

            MyMplCanvas.fig.canvas.mpl_connect('button_press_event', self.on_click)
            MyMplCanvas.fig.canvas.mpl_disconnect(MyMplCanvas.fig.canvas.mpl_connect('pick_event', self.on_pick))

    def get_company_num(self, x_data, y_data):
        for soldier in self.soldiers:
            if soldier.x == x_data and soldier.y == y_data:
                return soldier.company_number

    def on_click(self, event):
        x_data = event.xdata
        y_data = event.ydata
        if len(self.picked_soldier) > 0:
            soldier = self.picked_soldier.pop(0)
            soldier.update_location(x_data, y_data)

        print(x_data, y_data)
        MyMplCanvas.fig.canvas.mpl_connect('pick_event', self.on_pick)
        MyMplCanvas.fig.canvas.mpl_disconnect(MyMplCanvas.fig.canvas.mpl_connect('button_press_event', self.on_click))

    def on_hover(self, event):
        if event.inaxes == self.canvas.ax:
            for line in self.canvas.ax.lines:
                contains, index = line.contains(event)
                if contains:
                    self.tooltip.set_text(line.get_label())
                    self.tooltip.set_x(line.get_xdata())
                    self.tooltip.set_y(line.get_ydata())
                    #if self.c1.company_number == self.get_company_num(line.get_xdata(), line.get_ydata()):
                    self.tooltip.set_visible(True)
                    self.tooltip_coords = line.get_xdata(), line.get_ydata()
                    self.tooltip_text = line.get_label()
                    break
            else:
                self.tooltip.set_visible(False)
        self.tooltip_visible = self.tooltip._visible
        # redraw the canvas to display or hide the label
        self.canvas.draw()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    sys.exit(App.exec_())


