from Entities import Soldier, CompanyCommander, BTW, FieldObjects
import matplotlib.pylab as plt
import mplcursors
import matplotlib.animation as animation

#c1 = CompanyCommander(1, (5.2, 4.2), 100)
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
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
picked_soldier = []
company1 = []
company2 = []
company3 = []


def create_plot():
    for s in soldiers:
        if s.company_number == 1:
            company1.append(s)
            if type(s) == Soldier:
                ax.plot(s.x, s.y, marker='o', markersize=5, color="blue", picker=5, label=s.__str__())
            else:
                ax.plot(s.x, s.y, marker='*', markersize=5, color="blue", picker=5, label=s.__str__())

        elif s.company_number == 2:
            company2.append(s)
            if type(s) == Soldier:
                ax.plot(s.x, s.y, marker='o', markersize=5, color="red", picker=5, label=s.__str__())
            else:
                ax.plot(s.x, s.y, marker='*', markersize=5, color="red", picker=5, label=s.__str__())

        elif s.company_number == 3:
            company3.append(s)
            if type(s) == Soldier:
                ax.plot(s.x, s.y, marker='o', markersize=5, color="green", picker=5, label=s.__str__())
            else:
                ax.plot(s.x, s.y, marker='*', markersize=5, color="green", picker=5, label=s.__str__())
        else:
            continue

    mplcursors.cursor(hover=True, highlight=True).connect("add",
                                                          lambda sel: sel.annotation.set_text(sel.artist.get_label()))


def on_pick(event):
    this_point = event.artist
    x_data = this_point.get_xdata()
    y_data = this_point.get_ydata()
    ind = event.ind

    for soldier in soldiers:
        if soldier.x == x_data and soldier.y == y_data:
            index = soldier.ID - 1
            picked_soldier.append(soldier)
            break

    print(str(float(x_data[ind])) + ", " + str(float(y_data[ind])))
    print(str(soldiers[index].__str__()))

    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_disconnect(fig.canvas.mpl_connect('pick_event', on_pick))


def on_click(event):
    x_data = event.xdata
    y_data = event.ydata
    if len(picked_soldier) > 0:
        soldier = picked_soldier.pop(0)
        soldier.update_location(x_data, y_data)

    print(x_data, y_data)
    fig.canvas.mpl_connect('pick_event', on_pick)
    fig.canvas.mpl_disconnect(fig.canvas.mpl_connect('button_press_event', on_click))


def animate(self):
    ax.clear()
    create_plot()


fig.canvas.mpl_connect('pick_event', on_pick)
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

