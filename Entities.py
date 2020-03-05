import logging
import pickle
import random
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
import copy
import Utility

logger = Utility.setup_logger('field', 'field.log')


# FieldUDP
class FieldUDP:

    # Constructor
    def __init__(self):
        self.company1 = []
        self.company2 = []
        self.company3 = []

        self.forces = []

        self.enemies = []
        self.marked_enemies = []

        date_time = datetime.now().strftime("%d-%m-%Y.%H.%M.%S")

        self.scenario = FieldScenario(f"Field_Scenario.{date_time}", date_time)

        self.sock = Utility.get_field_sock()
        self.sock.bind(Utility.get_field_address())

        self.executor = ThreadPoolExecutor(max_workers=10)
        self.listen_thread = self.executor.submit(self.listen)
        self.report_thread = self.executor.submit(self.report_alive)
        self.check_for_enemies_thread = self.executor.submit(self.check_for_enemies)
        self.enemies_check_for_forces_thread = self.executor.submit(self.enemies_check_for_forces)
        self.enemy_attack_thread = self.executor.submit(self.enemy_attack)
        self.save_frames_thread = self.executor.submit(self.save_frames)

    def save_frames(self):
        while True:
            current = self.forces.copy()
            frame = Frame(datetime.now().strftime("%H:%M:%S"), current)
            try:
                self.scenario.save_frame(frame)
            except BaseException as exc:
                logger.error(exc)
            time.sleep(1)

    # listen() - Listening to incoming packets on background, while receiving a packet, it goes to receive_handler()
    # func to handle the message.
    def listen(self):
        print('Listening...')
        logger.debug('Listening...')

        while True:
            # set max size of message
            rec_packet, rec_address = self.sock.recvfrom(65527)

            # decoding the message to String
            rec_packet = pickle.loads(rec_packet)
            if rec_packet:
                self.receive_handler(rec_packet, rec_address)

    # check_for_enemies() - check for every field_object that in the field (forces list) if there is enemy (enemies)
    #                       in sight (if there is enemy located in his radius). if there is,
    def check_for_enemies(self):
        enemy_sight = 1
        lookout_sight = 2

        while True:
            for field_object in self.forces:
                enemies_in_sight = []

                for enemy in self.enemies:
                    # if STOP_FIELD_THREADS:
                    #     break

                    if enemy.get_type() == Utility.EnemyType.soldier.value or enemy.get_type() == Utility.EnemyType.launcher.value:
                        if (((enemy.get_x() - field_object.get_x()) ** 2) + (
                                (enemy.get_y() - field_object.get_y()) ** 2)) < (enemy_sight ** 2):
                            enemies_in_sight.append(enemy)
                    else:
                        if (((enemy.get_x() - field_object.get_x()) ** 2) + (
                                (enemy.get_y() - field_object.get_y()) ** 2)) < (lookout_sight ** 2):
                            enemies_in_sight.append(enemy)

                field_object.enemies_in_sight(enemies_in_sight)
                time.sleep(0.1)

    def enemies_check_for_forces(self):
        while True:
            for enemy in self.enemies:
                forces_in_sight = []
                if enemy.get_type() == Utility.EnemyType.launcher.value:
                    continue

                elif enemy.get_type() == Utility.EnemyType.lookout_point.value:
                    forces_sight = 2

                else:
                    forces_sight = 1

                for field_object in self.forces:

                    if (((enemy.get_x() - field_object.get_x()) ** 2) +
                        ((enemy.get_y() - field_object.get_y()) ** 2)) < (forces_sight ** 2):
                        forces_in_sight.append(field_object)

                enemy.forces_in_sight(forces_in_sight)
                time.sleep(0.1)

    def get_enemy(self, enemy):
        for e in self.enemies:
            if e.get_id() == enemy.get_id():
                return e
        return None

    def forces_attack(self, field_object, enemy):
        field_object = self.get_field_object(field_object.get_company_num(), field_object.get_id())
        enemy = self.get_enemy(enemy)

        field_object.attack_enemy(enemy)

        while True:
            if enemy is None:
                break

            if enemy != field_object.get_attacking_enemy():
                break
            if field_object.is_in_sight(enemy):
                field_object.set_move_to(None)
                while True:
                    if field_object.get_move_to_location() is not None or \
                            enemy is not field_object.get_attacking_enemy():
                        break

                    if field_object.get_type() == Utility.ObjectType.soldier.value:
                        damage = random.randint(-2, 10)
                    else:
                        damage = random.randint(-3, 20)
                    if damage < 0:
                        damage = 0
                    if field_object.get_ammo() <= 0:
                        break
                    field_object.shoot()
                    enemy.got_damage(damage)
                    if enemy.get_hp() <= 0:
                        field_object.attack_enemy(None)
                        self.enemies.remove(enemy)
                        break
                    time.sleep(1)

            else:
                if field_object.get_move_to_location() is not None:
                    continue
                else:
                    location = enemy.get_location()
                    field_object.set_move_to(location)

                    move_to_thread = threading.Thread(target=self.move_to,
                                                      args=(field_object, location[Utility.Location.X.value],
                                                            location[Utility.Location.Y.value]))
                    move_to_thread.start()

                    while enemy not in field_object.get_in_sight():

                        if enemy is not field_object.get_attacking_enemy() or \
                                location is not field_object.get_move_to_location():
                            break
                        time.sleep(0.5)

    def get_enemy_location(self, id):
        for enemy in self.enemies:
            if enemy.get_id() == id:
                return enemy.get_location()

    def enemy_attack(self):
        while True:
            for enemy in self.enemies:

                if enemy.get_type() is Utility.EnemyType.launcher.value or Utility.EnemyType.lookout_point.value:
                    continue

                if len(enemy.get_in_sight()) == 0 or enemy.get_ammo() <= 0:
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
                        packet = Packet(Utility.Sender.soldier.value, field_object.get_company_num(),
                                        Utility.Receiver.company_commander.value, Utility.MessageType.got_shot.value,
                                        message)
                        self.send_handler(packet)

                        save_message = Message(datetime.now().strftime("%H:%M:%S"), message)
                        self.scenario.save_message(save_message)

                time.sleep(1)
                enemy.not_shooting()

    # report_alive - A background function that reporting the status of the FieldObjects on the field status to their
    #                CompanyCommanders every 2 seconds by moving the packet it creates to the send_handler() func
    def report_alive(self):
        while True:
            updated_enemies = []

            for field_object in self.company1:

                if field_object.get_hp() <= 0:
                    self.company1.remove(field_object)

                message = AliveMessage(field_object)
                send_packet = Packet(Utility.Sender.soldier.value, field_object.get_company_num(),
                                     Utility.Receiver.company_commander.value,
                                     Utility.MessageType.alive.value, message)

                for enemy in field_object.get_in_sight():
                    if Utility.enemy_contain(updated_enemies, enemy.get_id()) == -1:
                        updated_enemies.append(enemy)

                        if enemy.get_type() == Utility.EnemyType.launcher or enemy.get_type() == Utility.EnemyType.lookout_point:
                            marked_enemy_index = Utility.enemy_contain(self.marked_enemies, enemy.get_id())
                            if marked_enemy_index == -1:
                                self.marked_enemies.append(enemy)
                            else:
                                self.marked_enemies[marked_enemy_index] = enemy

                time.sleep(0.100)

                self.send_handler(send_packet)

            for field_object in self.company2:

                if field_object.get_hp() <= 0:
                    self.company2.remove(field_object)

                message = AliveMessage(field_object)
                send_packet = Packet(Utility.Sender.soldier.value, field_object.get_company_num(),
                                     Utility.Receiver.company_commander.value,
                                     Utility.MessageType.alive.value, message)

                for enemy in field_object.get_in_sight():
                    if Utility.enemy_contain(updated_enemies, enemy.get_id()) == -1:
                        updated_enemies.append(enemy)

                        if enemy.get_type() == Utility.EnemyType.launcher or enemy.get_type() == Utility.EnemyType.lookout_point:
                            marked_enemy_index = Utility.enemy_contain(self.marked_enemies, enemy.get_id())
                            if marked_enemy_index == -1:
                                self.marked_enemies.append(enemy)
                            else:
                                self.marked_enemies[marked_enemy_index] = enemy

                time.sleep(0.100)

                self.send_handler(send_packet)

            for field_object in self.company3:

                if field_object.get_hp() <= 0:
                    self.company3.remove(field_object)

                message = AliveMessage(field_object)
                send_packet = Packet(Utility.Sender.soldier.value, field_object.get_company_num(),
                                     Utility.Receiver.company_commander.value,
                                     Utility.MessageType.alive.value, message)

                for enemy in field_object.get_in_sight():
                    if Utility.enemy_contain(updated_enemies, enemy.get_id()) == -1:
                        updated_enemies.append(enemy)

                        if enemy.get_type() == Utility.EnemyType.launcher or enemy.get_type() == Utility.EnemyType.lookout_point:
                            marked_enemy_index = Utility.enemy_contain(self.marked_enemies, enemy.get_id())
                            if marked_enemy_index == -1:
                                self.marked_enemies.append(enemy)
                            else:
                                self.marked_enemies[marked_enemy_index] = enemy

                time.sleep(0.100)

                self.send_handler(send_packet)

            time.sleep(0.100)

            updated_enemies = Utility.marked_enemies_check(updated_enemies, self.marked_enemies)

            message = EnemiesInSightMessage(updated_enemies)
            send_packet = Packet(Utility.Sender.soldier.value, Utility.Company.not_relevant.value,
                                 Utility.Receiver.company_commander.value,
                                 Utility.MessageType.enemies_in_sight.value, message)

            self.send_handler(send_packet)
            time.sleep(2.0)

    # get_field_object(company_num, id) - Func that returns the wanted FieldObject from his company list
    def get_field_object(self, company_num, id):
        if int(company_num) == Utility.Company.company1.value:
            for field_object in self.company1:
                if field_object.get_id() == int(id):
                    return field_object

        elif int(company_num) == Utility.Company.company2.value:
            for field_object in self.company2:
                if field_object.get_id() == int(id):
                    return field_object

        elif int(company_num) == Utility.Company.company3.value:
            for field_object in self.company3:
                if field_object.get_id() == int(id):
                    return field_object

        else:
            return -1

    # move_to(field_object, new_x, new_y) - while FieldUDP gets a MoveOrderMessage, the receive_handler() triggers the
    #                                       move_to() func. it moves the FieldObject, step by step by it's own speed
    def move_to(self, field_object, new_x, new_y):
        type = field_object.__class__.__name__
        if type is Soldier or type is APC:
            attacking_enemy = field_object.get_attacking_enemy()
        start_point = field_object.get_x(), field_object.get_y()
        end_point = float(new_x), float(new_y)
        while field_object.get_move_to_location() == end_point:
            if type is Soldier or type is APC:
                if attacking_enemy != field_object.get_attacking_enemy():
                    break
            if end_point == (field_object.get_x(), field_object.get_y()):
                break

            steps = Utility.get_line(start_point, end_point)
            for step in steps:
                if end_point != field_object.get_move_to_location():
                    break
                time.sleep(field_object.get_speed())
                step_x = step[Utility.Location.X.value]
                step_y = step[Utility.Location.Y.value]
                field_object.update_location(step_x, step_y)
            if end_point != field_object.get_move_to_location():
                break
            time.sleep(field_object.get_speed())
            field_object.update_location(new_x, new_y)
        if end_point == field_object.get_move_to_location():
            field_object.set_move_to(None)

    # receive_handler(packet, address) - Receive the packet and the address that it came from, check the case and act
    #                                    according to the case
    def receive_handler(self, rec_packet, address):
        case = Utility.sender_receiver_switch_case(rec_packet)

        # CompanyCommander >> Soldier
        if case == Utility.Case.cc_to_soldier.value:
            opt_case = rec_packet.get_message_type()

            # Move Order message
            if opt_case == Utility.MessageType.move_order.value:
                message = rec_packet.get_message()
                location = message.get_new_location()
                new_x = location[Utility.Location.X.value]
                new_y = location[Utility.Location.Y.value]

                field_object = self.get_field_object(message.get_company_num(), message.get_field_object_id())
                field_object.set_move_to(location)

                move_to_thread = threading.Thread(target=self.move_to, args=(field_object, new_x, new_y))
                move_to_thread.start()

                # Create and send approval message
                message = MoveApprovalMessage(field_object, location, rec_packet.get_id())
                send_packet = Packet(Utility.Sender.soldier.value, field_object.get_company_num(),
                                     Utility.Receiver.company_commander.value,
                                     Utility.MessageType.move_approval.value, message)
                self.send_handler(send_packet)

                save_message = Message(datetime.now().strftime("%H:%M:%S"), message)
                self.scenario.save_message(save_message)

                logger.debug(
                    "Move approval message was sent from FieldObject #{} to CC #{}".format(field_object.get_id(),
                                                                                           field_object.get_company_num()))

            # Engage Order Message
            if opt_case == Utility.MessageType.engage_order.value:
                message = rec_packet.get_message()
                field_object = message.get_field_object()
                enemy = message.get_enemy()

                args = field_object, enemy

                forces_attack_thread = threading.Thread(target=self.forces_attack, args=args)
                field_object.set_move_to(None)
                forces_attack_thread.start()

                message = EngageApprovalMessage(field_object.get_company_num(), field_object.get_id(), enemy.get_id(),
                                                rec_packet.get_id())
                send_packet = Packet(Utility.Sender.soldier.value, field_object.get_company_num(),
                                     Utility.Receiver.company_commander.value,
                                     Utility.MessageType.engage_approval.value, message)

                self.send_handler(send_packet)

                save_message = Message(datetime.now().strftime("%H:%M:%S"), message)
                self.scenario.save_message(save_message)

                logger.debug(
                    f"Engage approval was sent from FieldObject #{field_object.get_id()} to CC #{field_object.get_company_num()}")


        # Error case
        else:
            logger.error(str(address) + " >> " + str(rec_packet))

    # send_handler(send_packet) - Sending the packet that it gets
    def send_handler(self, send_packet):
        cc_address = Utility.get_cc_address()
        bc_address = Utility.get_bc_address()
        try:
            byte_packet = pickle.dumps(send_packet)
            self.sock.sendto(byte_packet, cc_address)
            time.sleep(0.100)
            self.sock.sendto(byte_packet, bc_address)

        except:
            logger.error("The message '{}' didn't reached to CC".format(send_packet))
            print("The message '{}' did'nt reached to the Company Commander!!".format(send_packet))

    def add_to_forces(self, field_object):
        if field_object.get_company_num() is Utility.Company.company1.value:
            company = self.company1
        elif field_object.get_company_num() is Utility.Company.company2.value:
            company = self.company2
        elif field_object.get_company_num() is Utility.Company.company3.value:
            company = self.company3
        else:
            company = None

        company.append(field_object)
        self.forces = self.company1 + self.company2 + self.company3

    def add_to_enemies(self, enemy):
        self.enemies.append(enemy)

    def enemy_move_to(self, enemy, location):
        new_x = location[Utility.Location.X.value]
        new_y = location[Utility.Location.Y.value]

        enemy = self.get_enemy(enemy)
        enemy.set_move_to(location)

        move_to_thread = threading.Thread(target=self.move_to, args=(enemy, new_x, new_y))
        move_to_thread.start()

    def check_forces_attack(self, field_object, enemy):
        args = field_object, enemy
        forces_attack_thread = threading.Thread(target=self.forces_attack, args=args)
        field_object.set_move_to(None)
        forces_attack_thread.start()


# FieldObject
class FieldObjects:
    # Attributes
    ID = 1

    # Constructor
    def __init__(self, company_number, location, ammo):
        self.ID = FieldObjects.ID
        FieldObjects.ID += 1
        self.company_number = company_number
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.in_sight = []
        self.got_shot = False
        self.move_to_location = None
        self.attacking_enemy = None

    def is_in_sight(self, enemy):
        for e in self.in_sight:
            if e.get_id() == enemy.get_id():
                return True
            else:
                return False

    # toString
    def __str__(self):
        return "{} #{}: \n" \
               "Company Number: {} \n" \
               "Location: ({}, {}) \n" \
               "Ammo: {} \n" \
               "HP: {} \n".format(self.__class__.__name__, self.ID, self.company_number, "{0:.2f}".format(self.x),
                                  "{0:.2f}".format(self.y), self.ammo, self.HP)

    # Getters
    def get_company_num(self):
        return self.company_number

    def get_id(self):
        return self.ID

    def get_location(self):
        return self.x, self.y

    def get_str_location(self):
        return str(self.x) + ", " + str(self.y)

    def get_ammo(self):
        return self.ammo

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_in_sight(self):
        return self.in_sight

    def is_got_shot(self):
        return self.got_shot

    def get_move_to_location(self):
        return self.move_to_location

    def get_attacking_enemy(self):
        return self.attacking_enemy

    # Setters
    def set_move_to(self, location):
        self.move_to_location = location

    def attack_enemy(self, enemy):
        self.attacking_enemy = enemy

    # update_location(new_x, new_y) - update the FieldObject location
    def update_location(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def enemies_in_sight(self, enemies):
        self.in_sight = enemies

    # Got Damage
    def got_damage(self, damage):
        self.HP -= damage

    def got_shot_alert(self):
        self.got_shot = True
        time.sleep(5)
        self.got_shot = False

    def shoot(self):
        self.ammo = self.ammo - 1

    def set_in_sight(self, in_sight):
        self.in_sight = in_sight


# Soldier
class Soldier(FieldObjects):
    # Constructor
    def __init__(self, company_number, location, ammo):
        super().__init__(company_number, location, ammo)
        self.HP = 100
        self.speed = 1

    # Getters
    def get_speed(self):
        return self.speed

    def get_hp(self):
        return self.HP

    @staticmethod
    def get_type():
        return Utility.ObjectType.soldier.value


# APC
class APC(FieldObjects):
    # Constructor
    def __init__(self, company_number, location, ammo):
        super().__init__(company_number, location, ammo)
        self.HP = 1000
        self.speed = 2

    # Getters
    def get_speed(self):
        return self.speed

    def get_hp(self):
        return self.HP

    @staticmethod
    def get_type():
        return Utility.ObjectType.apc.value


# BattalionCommander
class BattalionCommander:
    def __init__(self):
        self.enemies = []
        self.commanders = []

    def update_enemies(self, enemies_list):
        self.enemies = enemies_list

    def get_enemies(self):
        return self.enemies

    def get_commanders(self):
        return self.commanders


# CompanyCommander
class CompanyCommander:
    # Attributes
    ID = 1

    # Constructor
    def __init__(self, company_number, location, ammo):
        self.ID = CompanyCommander.ID
        CompanyCommander.ID += 1
        self.company_number = company_number
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100
        self.revealed_enemies = []
        self.STOP_CC_THREADS = False

    # Getters
    def get_enemies(self):
        return self.revealed_enemies

    def is_stopped(self):
        return self.STOP_CC_THREADS

    def get_company_num(self):
        return self.company_number

    def get_id(self):
        return self.ID

    def get_location(self):
        return self.x, self.y

    def get_hp(self):
        return self.HP

    def get_ammo(self):
        return self.ammo

    # Setters
    def set_location(self, location):
        self.x = location[0]
        self.y = location[1]

    def set_company(self, company_num):
        self.company_number = company_num

    def update_enemies(self, enemies):
        self.revealed_enemies = enemies

    def stop(self):
        self.STOP_CC_THREADS = True


# Enemy
class Enemy:
    # Attributes
    ID = 1000

    # Constructor
    def __init__(self, location, ammo):
        self.ID = Enemy.ID
        Enemy.ID += 1
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.in_sight = []

    # Getters
    def get_id(self):
        return self.ID

    def get_location(self):
        return self.x, self.y

    def get_str_location(self):
        return str(self.x) + ", " + str(self.y)

    def get_ammo(self):
        return self.ammo

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_in_sight(self):
        return self.in_sight

    def forces_in_sight(self, forces):
        self.in_sight = forces


# EnemySoldier
class EnemySoldier(Enemy):
    def __init__(self, location, ammo):
        super().__init__(location, ammo)
        self.HP = 100
        self.speed = 2
        self.move_to_location = None
        self.shooting = False

    # Getters
    def get_move_to_location(self):
        return self.move_to_location

    def get_hp(self):
        return self.HP

    # Setters
    def set_location(self, location):
        self.x = location[0]
        self.y = location[1]

    def update_location(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def set_move_to(self, location):
        self.move_to_location = location

    def shoot(self):
        self.shooting = True
        self.ammo = self.ammo - 1

    def not_shooting(self):
        self.shooting = False

    def got_damage(self, damage):
        self.HP -= damage

    # Getters
    @staticmethod
    def get_type():
        return Utility.EnemyType.soldier.value

    def get_speed(self):
        return self.speed


# Launcher
class Launcher(Enemy):
    def __init__(self, location):
        super().__init__(location, 0)
        self.hp = 150

    # Getters
    @staticmethod
    def get_type():
        return Utility.EnemyType.launcher.value

    def get_hp(self):
        return self.hp

    def got_damage(self, damage):
        self.hp -= damage


# LookoutPoint
class LookoutPoint(Enemy):
    def __init__(self, location):
        super().__init__(location, 0)
        self.hp = 150

    # Getters
    @staticmethod
    def get_type():
        return Utility.EnemyType.lookout_point.value

    def get_hp(self):
        return self.hp

    def got_damage(self, damage):
        self.hp -= damage


# Scenario
class Scenario:
    def __init__(self, file_name, date_time):
        self.file_name = file_name
        self.date_time = date_time
        self.messages = []

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_date_time(self, date_time):
        self.date_time = date_time

    def save_message(self, message):
        self.messages.append(message)
        self.save()

    def save(self):
        with open(self.file_name, 'wb') as file:
            pickle.dump(self, file)
            file.close()

        # file = open("FieldScenarios/"+self.file_name, 'wb')
        # pickle.dump(self, file, 2)
        # file.close()

    # Getters
    def get_file_name(self):
        return self.file_name

    def get_messages(self):
        return self.messages

    def get_date_time(self):
        return self.date_time

    def get_message(self, date_time):
        return_message = []
        counter = 1
        for message in self.messages:
            t1 = datetime.strptime(message.get_time(), "%H:%M:%S")
            t2 = datetime.strptime(date_time, "%H:%M:%S")
            counter += 1
            if t1 > t2 or counter > len(self.messages):
                return return_message
            elif t1 == t2:
                return_message.append(message)
            else:
                continue


# FieldScenario
class FieldScenario(Scenario):
    def __init__(self, file_name=None, date_time=None):
        super().__init__("FieldScenarios/" + file_name, date_time)
        self.frames = []
        self.start_time = None
        self.end_time = None
        self.total_time = None
        self.time_in_sec = None

    def save_frame(self, frame):
        if len(self.frames) == 0:
            self.start_time = frame.get_time()
            self.end_time = frame.get_time()
        else:
            self.end_time = frame.get_time()

        self.total_time = datetime.strptime(self.end_time, "%H:%M:%S") - datetime.strptime(self.start_time, "%H:%M:%S")
        self.time_in_sec = self.total_time.seconds

        self.add_frame(frame)

        self.save()

    def fix_frames(self):
        current_time = datetime.strptime(self.start_time, "%H:%M:%S")
        for index in range(self.time_in_sec):
            if datetime.strptime(self.frames[index].get_time(), "%H:%M:%S") != current_time:
                new_frame = Frame(datetime.strftime(current_time, "%H:%M:%S"), self.frames[index-1].get_forces())
                self.frames.insert(index, new_frame)
            current_time += timedelta(seconds=1)

    # Getters
    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_total_time(self):
        return self.total_time

    def get_time_in_sec(self):
        return self.time_in_sec

    def get_frames(self):
        return self.frames

    def get_frame(self, date_time):
        for frame in self.frames:
            if frame.get_time() == date_time:
                return frame
        print(f"There is no time {date_time} in {self.file_name}")

    def add_frame(self, frame):
        self.frames.append(frame)


# CompanyCommanderScenario
class CompanyCommanderScenario(Scenario):
    def __init__(self, file_name=None, date_time=None, company_num=None, company_commander=None):
        if file_name is not None:
            file_name = "CompanyCommanderScenarios/" + file_name
        super().__init__(file_name, date_time)
        self.company_num = company_num
        self.company_commander = company_commander

    def set_company_num(self, company_num):
        self.company_num = company_num

    def set_company_commander(self, company_commander):
        self.company_commander = company_commander

    # Getters
    def get_company_num(self):
        return self.company_num

    def get_company_commander(self):
        return self.company_commander


# Frame
class Frame:
    def __init__(self, date_time, forces):
        self.date_time = date_time
        self.frame_forces = []
        self.create_new_forces(forces)
        self.enemies = []
        self.set_enemies()

    def set_enemies(self):
        for field_object in self.frame_forces:
            if len(field_object.get_in_sight()) > 0:
                for enemy in field_object.get_in_sight():
                    if enemy not in self.enemies:
                        self.enemies.append(enemy)

    # Getters
    def get_time(self):
        return self.date_time

    def get_forces(self):
        return self.frame_forces

    def get_enemies(self):
        return self.enemies

    def print_forces(self):
        string = ""
        for f in self.frame_forces:
            string += str(f.get_location())
        return string

    def __str__(self):
        return "date: " + self.get_time() + "\nforces:\n" + self.print_forces()

    def create_new_forces(self, forces):
        for field_object in forces:
            if field_object.get_type() is Utility.ObjectType.soldier.value:
                soldier = Soldier(field_object.get_company_num(), field_object.get_location(), field_object.get_ammo())
                soldier.set_in_sight(field_object.get_in_sight())
                self.frame_forces.append(soldier)
            elif field_object.get_type() is Utility.ObjectType.apc.value:
                apc = APC(field_object.get_company_num(), field_object.get_location(), field_object.get_ammo())
                apc.set_in_sight(field_object.get_in_sight())
                self.frame_forces.append(apc)
            else:
                pass


# Packet
class Packet:
    # Attributes
    ID = 1

    # Constructor
    def __init__(self, sender, company_num, receiver, message_type, message):
        self.ID = Packet.ID
        Packet.ID += 1
        self.sender = sender
        self.company_num = company_num
        self.receiver = receiver
        self.message_type = message_type
        self.message = message

    # Getters
    def get_id(self):
        return self.ID

    def get_sender(self):
        return self.sender

    def get_company_num(self):
        return self.company_num

    def get_receiver(self):
        return self.receiver

    def get_message_type(self):
        return self.message_type

    def get_message(self):
        return self.message

    # toString
    def __str__(self):

        if self.sender == Utility.Sender.soldier.value:
            sender = "Soldier"
        elif self.sender == Utility.Sender.company_commander.value:
            sender = "CC"
        else:
            sender = "BC"

        if self.receiver == Utility.Receiver.soldier.value:
            receiver = "Soldier"
        elif self.receiver == Utility.Receiver.company_commander.value:
            receiver = "CC"
        else:
            receiver = "BC"

        if self.message_type == Utility.MessageType.alive.value:
            message_type = "Alive"
        elif self.message_type == Utility.MessageType.move_order.value:
            message_type = "Move Order"
        else:
            message_type = "Engage Order"

        return "[ #{}. Sender: {}, Company: {}, Receiver: {}, Message Type: {}, Message: {} ]".format(self.ID,
                                                                                                      sender,
                                                                                                      self.company_num,
                                                                                                      receiver,
                                                                                                      message_type,
                                                                                                      self.message)


# AliveMessage
class AliveMessage:
    # Constructor
    def __init__(self, field_object):
        self.field_object = field_object

    # toString
    def __str__(self):
        return "|| ID: {}, Company: {}, Location: ({}), HP: {}, Ammo: {} ||".format(self.field_object.get_id(),
                                                                                    self.field_object.get_company_num(),
                                                                                    self.field_object.get_location(),
                                                                                    self.field_object.get_hp(),
                                                                                    self.field_object.get_ammo())

    # Getters
    def get_field_object(self):
        return self.field_object

    @staticmethod
    def get_type():
        return Utility.MessageType.alive.value


# MoveApprovalMessage
class MoveApprovalMessage:
    # Constructor
    def __init__(self, field_object, location, packet_id):
        self.field_object = field_object
        self.location = location
        self.approval_packet_id = packet_id

    def set_approval_packet_id(self, packet_id):
        self.approval_packet_id = id

    # Getters
    def get_field_object(self):
        return self.field_object

    def get_move_to_location(self):
        return self.location

    def get_approval_packet_id(self):
        return self.approval_packet_id

    @staticmethod
    def get_type():
        return Utility.MessageType.move_approval.value


# EnemiesInSightMessage
class EnemiesInSightMessage:
    # Constructor
    def __init__(self, enemies):
        self.enemies = enemies

    # Getters
    def get_enemies(self):
        return self.enemies

    @staticmethod
    def get_type():
        return Utility.MessageType.enemies_in_sight.value


# MoveOrderMessage
class MoveOrderMessage:
    # Constructor
    def __init__(self, company_num, field_object_id, location):
        self.company_num = company_num
        self.field_object_id = field_object_id
        self.location = location

    # Getters
    def get_company_num(self):
        return self.company_num

    def get_field_object_id(self):
        return self.field_object_id

    def get_new_location(self):
        return self.location

    # toString
    def __str__(self):
        return "|| Company: {}, ID: {}, MoveTo Location: ({}) ||".format(self.company_num,
                                                                         self.field_object_id,
                                                                         self.location)

    @staticmethod
    def get_type():
        return Utility.MessageType.move_order.value


# EngageOrderMessage
class EngageOrderMessage:
    # Constructor
    def __init__(self, field_object, enemy):
        self.field_object = field_object
        self.enemy = enemy

    # Getters
    def get_field_object(self):
        return self.field_object

    def get_enemy(self):
        return self.enemy

    @staticmethod
    def get_type():
        return Utility.MessageType.engage_order.value


# EngageApprovalMessage
class EngageApprovalMessage:
    # Constructor
    def __init__(self, company_num, field_object_id, enemy_id, packet_id):
        self.company_num = company_num
        self.field_object_id = field_object_id
        self.enemy_id = enemy_id
        self.approval_packet_id = packet_id

    def set_approval_packet_id(self, packet_id):
        self.approval_packet_id = id

    # Getters
    def get_company_num(self):
        return self.company_num

    def get_field_object_id(self):
        return self.field_object_id

    def get_enemy_id(self):
        return self.enemy_id

    def get_approval_packet_id(self):
        return self.approval_packet_id

    @staticmethod
    def get_type():
        return Utility.MessageType.engage_approval.value


# GotShotMessage
class GotShotMessage:
    # Constructor
    def __init__(self, field_object):
        self.field_object = field_object

    def get_field_object(self):
        return self.field_object

    @staticmethod
    def get_type():
        return Utility.MessageType.got_shot.value


# NotApprovedMessage
class NotApprovedMessage:
    # Constructor
    def __init__(self, field_object_id, company_num):
        self.field_object_id = field_object_id
        self.company_num = company_num

    def get_field_object_id(self):
        return self.field_object_id

    def get_company_num(self):
        return self.company_num

    @staticmethod
    def get_type():
        return Utility.MessageType.not_approved_message.value


# Message:
class Message:
    def __init__(self, date_time, message):
        self.date_time = date_time
        self.message = message
        self.colored_msg = None
        self.set_colored(message)

    def set_colored(self, message):

        if message.get_type() is Utility.MessageType.move_order.value:
            field_object_id = message.get_field_object_id()
            location = message.get_new_location()
            msg = "[ " + self.date_time + " ]" + "  " + \
                  f"CC #{message.get_company_num()} sent Move Order message ({location}) to" \
                  f"#{field_object_id}<br />"

            self.colored_msg = "<span style=\" font-size:8pt; font-weight:400; color:#000000;\" >"
            self.colored_msg += msg
            self.colored_msg += "</span>"

        elif message.get_type() is Utility.MessageType.move_approval.value:
            msg = "[ " + self.date_time + " ]" + "  " + f"#{message.get_field_object().get_id()} started moving <br />"

            self.colored_msg = "<span style=\" font-size:8pt; font-weight:400; color:#000000;\" >"
            self.colored_msg += msg
            self.colored_msg += "</span>"

        elif message.get_type() is Utility.MessageType.engage_order.value:
            field_object = message.get_field_object()
            msg = "[ " + self.date_time + " ]" + "  " + \
                  f"CC #{field_object.get_company_num()} sent Engage Order message to" \
                  f"#{message.get_field_object().get_id()}<br />"

            self.colored_msg = "<span style=\" font-size:8pt; font-weight:400; color:#000000;\" >"
            self.colored_msg += msg
            self.colored_msg += "</span>"

        elif message.get_type() is Utility.MessageType.engage_approval.value:
            msg = "[ " + self.date_time + " ]" + "  " + f"#{message.get_field_object_id()} started engaging target <br />"

            self.colored_msg = "<span style=\" font-size:8pt; font-weight:400; color:#000000;\" >"
            self.colored_msg += msg
            self.colored_msg += "</span>"

        elif message.get_type() is Utility.MessageType.got_shot.value:
            msg = "[ " + self.date_time + " ]" + " " + f"#{message.get_field_object()} got shot <br />"

            self.colored_msg = "<span style=\" font-size:8pt; font-weight:400; color:#ff0000;\" >"
            self.colored_msg += msg
            self.colored_msg += "</span>"

        elif message.get_type() is Utility.MessageType.not_approved_message.value:
            msg = "[ " + self.date_time + " ]" + "  " + f"Soldier #{message.get_field_object_id()} " \
                                                   f"didn't approved the {message.get_type()} <br />"

            self.colored_msg = "<span style=\" font-size:8pt; font-weight:500; color:#940913;\" >"
            self.colored_msg += msg
            self.colored_msg += "</span>"

    def get_message(self):
        return self.message

    def get_time(self):
        return self.date_time

    def get_colored_msg(self):
        return self.colored_msg

