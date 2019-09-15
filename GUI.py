import sys
from Entities import Soldier, CompanyCommander
from PyQt5 import QtCore, QtWidgets, uic
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
matplotlib.use('QT5Agg')


class MyWindow(QtWidgets.QMainWindow):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    soldiers = []
    picked_soldier = []

    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('qt_designer.ui', self)

        s1 = Soldier(1, (3, 4), 100)
        s2 = Soldier(2, (5, 6), 100)
        s3 = Soldier(3, (1, 6), 100)
        s4 = Soldier(1, (2, 3), 100)
        s5 = Soldier(2, (3, 3.5), 100)
        s6 = Soldier(3, (4.2, 3.7), 100)
        s7 = Soldier(1, (5.3, 4), 100)
        s8 = Soldier(2, (2.6, 4.3), 100)
        s9 = Soldier(3, (7, 5.2), 100)

        MyWindow.soldiers.append(s1)
        MyWindow.soldiers.append(s2)
        MyWindow.soldiers.append(s3)
        MyWindow.soldiers.append(s4)
        MyWindow.soldiers.append(s5)
        MyWindow.soldiers.append(s6)
        MyWindow.soldiers.append(s7)
        MyWindow.soldiers.append(s8)
        MyWindow.soldiers.append(s9)


        # x_list = []
        # y_list = []

        # for soldier in soldiers:
        #     x_list.append(soldier.x)
        #     y_list.append(soldier.y)

        for s in MyWindow.soldiers:
            if s.companyNumber == 1:
                MyWindow.ax.plot(s.x, s.y, marker='o', markersize=5, color="blue", picker=5)

            elif s.companyNumber == 2:
                MyWindow.ax.plot(s.x, s.y, marker='o', markersize=5, color="red", picker=5)

            elif s.companyNumber == 3:
                MyWindow.ax.plot(s.x, s.y, marker='o', markersize=5, color="green", picker=5)

        self.plotWidget = FigureCanvas(MyWindow.fig)
        lay = QtWidgets.QVBoxLayout(self.content_plot)
        self.toolbar = NavigationToolbar(self.plotWidget, self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.plotWidget)
        lay.addWidget(self.toolbar)

        MyWindow.fig.canvas.mpl_connect('pick_event', MyWindow.on_pick)
        #MyWindow.fig.canvas.mpl_connect('button_press_event', MyWindow.on_click)

    def on_pick(event):
        if len(MyWindow.picked_soldier) == 0:
            this_point = event.artist
            x_data = this_point.get_xdata()
            y_data = this_point.get_ydata()
            ind = event.ind
            index = -1

            for soldier in MyWindow.soldiers:
                if soldier.x == x_data and soldier.y == y_data:
                    index = soldier.ID - 1
                    MyWindow.picked_soldier.append(soldier)
                    break

            MyWindow.soldiers[index].pick()

            print(str(float(x_data[ind])) + ", " + str(float(y_data[ind])))
            print(str(MyWindow.soldiers[index].to_string()))

            MyWindow.fig.canvas.mpl_connect('button_press_event', MyWindow.on_click)
            MyWindow.fig.canvas.mpl_disconnect(MyWindow.fig.canvas.mpl_connect('pick_event', MyWindow.on_pick))



    def on_click(event):
        x_data = event.xdata
        y_data = event.ydata

        if len(MyWindow.picked_soldier) > 0:
            soldier = MyWindow.picked_soldier.pop(0)
            soldier.update_location(x_data, y_data)
            soldier.unpick()
            print(soldier.get_location())

        print(x_data, y_data, len(MyWindow.picked_soldier))
        MyWindow.fig.canvas.mpl_connect('pick_event', MyWindow.on_pick)
        MyWindow.fig.canvas.mpl_disconnect(MyWindow.fig.canvas.mpl_connect('button_press_event', MyWindow.on_click))

    def soldier_index(x_data, y_data):
        for soldier in MyWindow.soldiers:
            if soldier.x == x_data and soldier.y == y_data:
                return soldier.ID - 1


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

main()



