import random
import threading
import time
from Entities import FieldUDP, Soldier, APC, EnemySoldier, LookoutPoint, Launcher
from Utility import EnemyType

fieldUDP = FieldUDP()

enemies = []

enemy = Launcher((2, 2))
fieldUDP.add_to_enemies(enemy)
enemies.append(enemy)


def random_forces_location():
    x = random.uniform(0.5, 15)
    y = random.uniform(0.5, 7.5)

    return x, y


def random_enemies_location():

    x = 100
    y = 100

    while x > 20.5 and y > 11.5 or x is None and y is None:
        x = random.uniform(15, 24.5)
        y = random.uniform(7.5, 14.5)

    return x, y


# Initialize Soldiers and APCs
# Company 1
for i in range(5):
    fieldUDP.add_to_forces(Soldier(1, random_forces_location(), 100))

fieldUDP.add_to_forces(APC(1, random_forces_location(), 200))

# Company 2
for i in range(5):
    fieldUDP.add_to_forces(Soldier(2, random_forces_location(), 100))

fieldUDP.add_to_forces(APC(2, random_forces_location(), 200))

# Company 3
for i in range(5):
    fieldUDP.add_to_forces(Soldier(3, random_forces_location(), 100))

fieldUDP.add_to_forces(APC(3, random_forces_location(), 200))

# Enemies
# Enemy Soldiers
# for i in range(10):
#     enemy = EnemySoldier(random_enemies_location(), 200)
#     fieldUDP.add_to_enemies(enemy)
#     enemies.append(enemy)


# Lookout Point
# for i in range(2):
#     location = random_enemies_location()
#     enemy = LookoutPoint(location, EnemySoldier(location, 150))
#     fieldUDP.add_to_enemies(enemy)
#     enemies.append(enemy)
#
# for i in range(3):
#     enemy = Launcher(random_enemies_location())
#     fieldUDP.add_to_enemies(enemy)
#     enemies.append(enemy)
#
#
# def enemies_movement():
#     while True:
#         for e in enemies:
#             time.sleep(10)
#             if e.get_type() is EnemyType.launcher.value or e.get_type() is EnemyType.lookout_point.value:
#                 continue
#             else:
#                 if e.get_move_to_location() is None:
#                     fieldUDP.enemy_move_to(e, random_forces_location())
#                 else:
#                     continue




# enemies_movement_thread = threading.Thread(target=enemies_movement)
# enemies_movement_thread.start()





