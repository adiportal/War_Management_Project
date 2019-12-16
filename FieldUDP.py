import random
import logging
import threading
import time
import pickle
from Entities import Packet, Soldier, BTW, AliveMessage, EnemySoldier, LookoutPoint, EnemiesInSightMessage, \
                     MoveApprovalMessage, GotShotMessage
from Utility import Company, Sender, Receiver, MessageType, Case, Location, get_line, get_cc_address, \
    get_field_sock, get_field_address, EnemyType, enemy_contain, marked_enemies_check, \
    sender_receiver_switch_case, ObjectType, get_bc_receive_address, get_bc_address

global STOP_FIELD_THREADS
STOP_FIELD_THREADS = False


# Initialize the Logger
logging.basicConfig(filename='FieldLog.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : '
                                                                         'Soldier : %(message)s')

# Initialize Companies
company1 = []
company2 = []
company3 = []


# Initialize Soldiers and BTWs
# Company 1
s1 = Soldier(1, (2, 1.5), 25)
s2 = Soldier(1, (13, 8), 25)
s3 = Soldier(1, (7, 3), 25)
s4 = Soldier(1, (9, 1), 25)
s5 = Soldier(1, (12, 7), 25)

btw1 = BTW(1, (2, 9), 50)


# Company 2
s6 = Soldier(2, (3.56, 2), 25)
s7 = Soldier(2, (6.6787, 0.677), 25)
s8 = Soldier(2, (1.7878, 6.2), 25)
s9 = Soldier(2, (9.456, 7.88), 25)
s10 = Soldier(2, (10.41, 5.667), 25)

btw2 = BTW(2, (12, 4), 50)

# Company 3
s11 = Soldier(3, (5.387, 5.888), 25)
s12 = Soldier(3, (4.123, 2.222), 25)
s13 = Soldier(3, (3.7878, 7.777), 25)
s14 = Soldier(3, (5.222, 1.56), 25)
s15 = Soldier(3, (7.8, 3.6), 25)

btw3 = BTW(3, (6.872, 6.999), 50)

# Adding FieldObjects to their companies
company1 = [s1, s2, s3, s4, s5, btw1]
company2 = [s6, s7, s8, s9, s10, btw2]
company3 = [s11, s12, s13, s14, s15, btw3]

forces = company1 + company2 + company3

# Enemies
es1 = EnemySoldier((2, 0.4), 100)

enemies = [es1]
marked_enemies = []


# listen() - Listening to incoming packets on background, while receiving a packet, it goes to receive_handler() func
#            to handle the message.
def listen():
    print('Listening...')
    logging.debug('Listening...')

    while True:
        # set max size of message
        rec_packet, rec_address = sock.recvfrom(65527)

        # decoding the message to String
        rec_packet = pickle.loads(rec_packet)
        if rec_packet:
            receive_handler(rec_packet, rec_address)

        if STOP_FIELD_THREADS:
            logging.debug("Closing FieldUDP...")
            break


# check_for_enemies() - check for every field_object that in the field (forces list) if there is enemy (enemies)
#                       in sight (if there is enemy located in his radius). if there is,
def check_for_enemies():
    enemy_sight = 1
    lookout_sight = 2

    while True:
        for field_object in forces:
            enemies_in_sight = []

            for enemy in enemies:
                if STOP_FIELD_THREADS:
                    break

                if enemy.get_type() == EnemyType.soldier.value or enemy.get_type() == EnemyType.launcher.value:
                    if (((enemy.get_x() - field_object.get_x()) ** 2) + ((enemy.get_y() - field_object.get_y()) ** 2)) < (enemy_sight ** 2):
                        enemies_in_sight.append(enemy)
                else:
                    if (((enemy.get_x() - field_object.get_x()) ** 2) + ((enemy.get_y() - field_object.get_y()) ** 2)) < (lookout_sight ** 2):
                        enemies_in_sight.append(enemy)

            field_object.enemies_in_sight(enemies_in_sight)


def enemies_check_for_forces():
    while True:
        for enemy in enemies:
            forces_in_sight = []
            if enemy.get_type() == EnemyType.launcher.value:
                continue

            elif enemy.get_type() == EnemyType.lookout_point.value:
                forces_sight = 2

            else:
                forces_sight = 1

            for field_object in forces:
                if STOP_FIELD_THREADS:
                    break

                if (((enemy.get_x() - field_object.get_x()) ** 2) +
                   ((enemy.get_y() - field_object.get_y()) ** 2)) < (forces_sight ** 2):
                    forces_in_sight.append(field_object)

            enemy.forces_in_sight(forces_in_sight)


def forces_attack(field_object, enemy):
    print("got engage order'")

    if enemy.get_type() == EnemyType.lookout_point.value:
        enemy = enemy.get_soldier()

    if field_object.get_type() == ObjectType.soldier.value:
        damage = random.randint(-2, 10)
    else:
        damage = random.randint(-3, 20)
    if damage < 0:
        damage = 0

    field_object.attack_enemy(enemy)

    while enemy.get_hp() > 0:

        if enemy != field_object.get_attacking_enemy():
            break

        if enemy in field_object.get_in_sight():
            field_object.set_move_to(None)
            while True:
                if field_object.get_move_to_location() is not None or \
                   enemy is not field_object.get_attacking_enemy():
                    break

                field_object.shoot()
                enemy.got_damage(damage)
                print(enemy.get_hp())
                if enemy.get_hp() <= 0:
                    field_object.attack_enemy(None)
                    enemies.remove(enemy)
                    break
                time.sleep(1)

        else:
            if field_object.get_move_to_location() is not None:
                continue
            else:
                location = enemy.get_location()
                field_object.set_move_to(location)

                move_to_thread = threading.Thread(target=move_to, args=(field_object, location[Location.X.value],
                                                                        location[Location.Y.value]))
                move_to_thread.start()

                while enemy not in field_object.get_in_sight():

                    if enemy is not field_object.get_attacking_enemy() or \
                       location is not field_object.get_move_to_location():
                        break
                    time.sleep(0.5)


def enemy_attack():
    while True:
        for enemy in enemies:
            if len(enemy.get_in_sight()) == 0:
                enemy.not_shooting()
                continue
            else:
                damage = random.randint(-2, 10)
                if damage < 0:
                    damage = 0

                field_object = random.choice(enemy.get_in_sight())

                enemy.shoot()
                field_object.got_damage(damage)

                if not field_object.is_got_shot():
                    field_object.got_shot_alert()
                    message = GotShotMessage(field_object)
                    packet = Packet(Sender.soldier.value, field_object.get_company_num(),
                                    Receiver.company_commander.value, MessageType.got_shot.value, message)
                    send_handler(packet)

                time.sleep(1)
            enemy.not_shooting()


# report_alive - A background function that reporting the status of the FieldObjects on the field status to their
#                CompanyCommanders every 2 seconds by moving the packet it creates to the send_handler() func
def report_alive():
    while True:
        updated_enemies = []

        for field_object in company1:

            if field_object.get_hp() <= 0:
                company1.remove(field_object)

            message = AliveMessage(field_object)
            send_packet = Packet(Sender.soldier.value, field_object.get_company_num(), Receiver.company_commander.value,
                                 MessageType.alive.value, message)

            for enemy in field_object.get_in_sight():
                if enemy_contain(updated_enemies, enemy.get_id()) == -1:
                    updated_enemies.append(enemy)

                    if enemy.get_type() == EnemyType.launcher or enemy.get_type() == EnemyType.lookout_point:
                        marked_enemy_index = enemy_contain(marked_enemies, enemy.get_id())
                        if marked_enemy_index == -1:
                            marked_enemies.append(enemy)
                        else:
                            marked_enemies[marked_enemy_index] = enemy

            time.sleep(0.100)

            send_handler(send_packet)

        for field_object in company2:

            if field_object.get_hp() <= 0:
                company2.remove(field_object)

            message = AliveMessage(field_object)
            send_packet = Packet(Sender.soldier.value, field_object.get_company_num(), Receiver.company_commander.value,
                                 MessageType.alive.value, message)

            for enemy in field_object.get_in_sight():
                if enemy_contain(updated_enemies, enemy.get_id()) == -1:
                    updated_enemies.append(enemy)

                    if enemy.get_type() == EnemyType.launcher or enemy.get_type() == EnemyType.lookout_point:
                        marked_enemy_index = enemy_contain(marked_enemies, enemy.get_id())
                        if marked_enemy_index == -1:
                            marked_enemies.append(enemy)
                        else:
                            marked_enemies[marked_enemy_index] = enemy

            time.sleep(0.100)

            send_handler(send_packet)

        for field_object in company3:

            if field_object.get_hp() <= 0:
                company3.remove(field_object)

            message = AliveMessage(field_object)
            send_packet = Packet(Sender.soldier.value, field_object.get_company_num(), Receiver.company_commander.value,
                                 MessageType.alive.value, message)

            for enemy in field_object.get_in_sight():
                if enemy_contain(updated_enemies, enemy.get_id()) == -1:
                    updated_enemies.append(enemy)

                    if enemy.get_type() == EnemyType.launcher or enemy.get_type() == EnemyType.lookout_point:
                        marked_enemy_index = enemy_contain(marked_enemies, enemy.get_id())
                        if marked_enemy_index == -1:
                            marked_enemies.append(enemy)
                        else:
                            marked_enemies[marked_enemy_index] = enemy

            time.sleep(0.100)

            send_handler(send_packet)

        time.sleep(0.100)

        updated_enemies = marked_enemies_check(updated_enemies, marked_enemies)

        message = EnemiesInSightMessage(updated_enemies)
        send_packet = Packet(Sender.soldier.value, Company.not_relevant.value, Receiver.company_commander.value,
                             MessageType.enemies_in_sight.value, message)

        send_handler(send_packet)
        time.sleep(2.0)


# get_field_object(company_num, id) - Func that returns the wanted FieldObject from his company list
def get_field_object(company_num, id):
    if int(company_num) == Company.company1.value:
        for field_object in company1:
            if field_object.get_id() == int(id):
                return field_object

    elif int(company_num) == Company.company2.value:
        for field_object in company2:
            if field_object.get_id() == int(id):
                return field_object

    elif int(company_num) == Company.company3.value:
        for field_object in company3:
            if field_object.get_id() == int(id):
                return field_object

    else:
        return -1


# get_enemy(id) - get the enemy from enemies list by the id
def get_enemy(id):
    for enemy in enemies:
        if enemy.get_id() == id:
            return enemy

    return -1


# move_to(field_object, new_x, new_y) - while FieldUDP gets a MoveOrderMessage, the receive_handler() triggers the
#                                       move_to() func. it moves the FieldObject, step by step by it's own speed
def move_to(field_object, new_x, new_y):
    start_point = field_object.get_x(), field_object.get_y()
    end_point = float(new_x), float(new_y)
    while True:
        steps = get_line(start_point, end_point)
        for step in steps:
            if end_point != field_object.get_move_to_location():
                break
            time.sleep(field_object.get_speed())
            step_x = step[Location.X.value]
            step_y = step[Location.Y.value]
            field_object.update_location(step_x, step_y)
        if end_point != field_object.get_move_to_location():
            break
        time.sleep(field_object.get_speed())
        field_object.update_location(new_x, new_y)
    if end_point == field_object.get_move_to_location():
        field_object.set_move_to(None)


# receive_handler(packet, address) - Receive the packet and the address that it came from, check the case and act
#                                    according to the case
def receive_handler(rec_packet, address):
    case = sender_receiver_switch_case(rec_packet)

    # CompanyCommander >> Soldier
    if case == Case.cc_to_soldier.value:
        opt_case = rec_packet.get_message_type()

        # Move Order message
        if opt_case == MessageType.move_order.value:
            message = rec_packet.get_message()
            location = message.get_new_location()
            new_x = location[Location.X.value]
            new_y = location[Location.Y.value]

            field_object = get_field_object(message.get_company_num(), message.get_field_object_id())
            field_object.set_move_to(location)

            move_to_thread = threading.Thread(target=move_to, args=(field_object, new_x, new_y))
            move_to_thread.start()

            # Create and send approval message
            message = MoveApprovalMessage(field_object, location)
            send_packet = Packet(Sender.soldier.value, field_object.get_company_num(), Receiver.company_commander.value,
                                 MessageType.move_approval.value, message)
            send_handler(send_packet)
            logging.debug("Move approval message was sent from FieldObject #{} to CC #{}".format(field_object.get_id(),
                                                                                        field_object.get_company_num()))

        # Engage Order Message
        if opt_case == MessageType.engage_order.value:
            message = rec_packet.get_message()
            enemy_id = message.get_enemy().get_id()
            field_object = get_field_object(message.get_company_num(), message.get_field_object_id())
            enemy = get_enemy(enemy_id)

            enemies_in_sight = field_object.get_in_sight()
            if enemy in enemies_in_sight:
                field_object.set_move_to(None)
                forces_attack(field_object, enemy)



    # Error case
    else:
        print(str(address) + " >> " + rec_packet)
        logging.error(str(address) + " >> " + rec_packet)


# send_handler(send_packet) - Sending the packet that it gets
def send_handler(send_packet):
    cc_address = get_cc_address()
    bc_address = get_bc_address()
    try:
        byte_packet = pickle.dumps(send_packet)
        sock.sendto(byte_packet, cc_address)
        time.sleep(0.100)
        sock.sendto(byte_packet, bc_address)

    except:
        logging.error("The message '{}' didn't reached to CC".format(send_packet))
        print("The message '{}' did'nt reached to the Company Commander!!".format(send_packet))


# **Main**
# Initiate Socket
sock = get_field_sock()

# Binding Socket
sock.bind(get_field_address())

# Initiate and Start listen and report_location threads
listen_thread = threading.Thread(target=listen)
report_thread = threading.Thread(target=report_alive)
check_for_enemies_thread = threading.Thread(target=check_for_enemies)
enemies_check_for_forces_thread = threading.Thread(target=enemies_check_for_forces)
enemy_attack_thread = threading.Thread(target=enemy_attack)

listen_thread.start()
report_thread.start()
check_for_enemies_thread.start()
enemies_check_for_forces_thread.start()
enemy_attack_thread.start()

time.sleep(5)

# args = s1, es1
#
# attack_thread = threading.Thread(target=forces_attack, args=args)
# attack_thread.start()


