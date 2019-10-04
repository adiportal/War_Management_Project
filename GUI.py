
import sys
import matplotlib
from mpldatacursor import datacursor

matplotlib.use('Qt5Agg')
import mplcursors
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, \
    QTextBrowser, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from Entities import Soldier, CompanyCommander, BTW, FieldObjects



class MyMplCanvas(FigureCanvas):
    fig = Figure(figsize=(5, 4), dpi=200)
    ax = fig.add_subplot(1, 1, 1)
    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"))
    annot.set_visible(False)

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

    soldiers = [s1, s2, s3, s4, s5, s6, s7, s8, s9]


    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        self.main_widget = QtWidgets.QWidget(self)

        vbox = QtWidgets.QVBoxLayout(self.main_widget)

        self.canvas = MyMplCanvas(self.main_widget)  ###attention###
        vbox.addWidget(self.canvas)

        hbox = QtWidgets.QHBoxLayout(self.main_widget)

        self.setLayout(vbox)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.tooltip_visible = False
        self.tooltip_coords = 0, 0
        self.tooltip_text = ''

        self.ani = FuncAnimation(self.canvas.figure, self.animate, interval=1000, blit=False)
        self.canvas.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def animate(self, i):
        self.canvas.ax.clear()
        self.tooltip = self.canvas.ax.annotate(self.tooltip_text, self.tooltip_coords, xytext=(20, 20),
                                               textcoords="offset points",
                                               size=8, bbox=dict(facecolor='yellow', boxstyle="round"),
                                               arrowprops=dict(shrink=0.05, facecolor='black', width=3, headlength=8))
        self.tooltip.set_visible(self.tooltip_visible)
        self.create_plot()

    def create_plot(self):
        for s in self.soldiers:
            if s.company_number == 1:
                if type(s) == Soldier:
                    self.canvas.ax.plot(s.x, s.y, marker='o', markersize=5, color="blue", picker=5, label=s.__str__())
                else:
                    self.canvas.ax.plot(s.x, s.y, marker='*', markersize=5, color="blue", picker=5, label=s.__str__())

            elif s.company_number == 2:
                if type(s) == Soldier:
                    self.canvas.ax.plot(s.x, s.y, marker='o', markersize=5, color="red", picker=5, label=s.__str__())
                else:
                    self.canvas.ax.plot(s.x, s.y, marker='*', markersize=5, color="red", picker=5, label=s.__str__())

            elif s.company_number == 3:
                if type(s) == Soldier:
                    self.canvas.ax.plot(s.x, s.y, marker='o', markersize=5, color="green", picker=5, label=s.__str__())
                else:
                    self.canvas.ax.plot(s.x, s.y, marker='*', markersize=5, color="green", picker=5, label=s.__str__())
            else:
                continue

    def on_pick(self, event):
        this_point = event.artist
        x_data = this_point.get_xdata()
        y_data = this_point.get_ydata()
        ind = event.ind

        for soldier in ApplicationWindow.soldiers:
            if soldier.x == x_data and soldier.y == y_data:
                index = soldier.ID - 1
                ApplicationWindow.picked_soldier.append(soldier)
                break

        print(str(float(x_data[ind])) + ", " + str(float(y_data[ind])))
        print(str(ApplicationWindow.soldiers[index].__str__()))

        MyMplCanvas.fig.canvas.mpl_connect('button_press_event', self.on_click)
        MyMplCanvas.fig.canvas.mpl_disconnect(MyMplCanvas.fig.canvas.mpl_connect
                                                           ('pick_event', self.on_pick))

    def on_click(self, event):
        x_data = event.xdata
        y_data = event.ydata
        if len(ApplicationWindow.picked_soldier) > 0:
            soldier = ApplicationWindow.picked_soldier.pop(0)
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


