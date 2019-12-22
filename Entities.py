import logging
import pickle
import random
import threading
import time
import Utility


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
               "HP: {} \n".format(self.__class__.__name__, self.ID, self.company_number, self.x, self.y, self.ammo,
                                  self.HP)

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
    ID = 1

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
        self.speed = 1
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
        self.HP = 150

    # Getters
    @staticmethod
    def get_type():
        return Utility.EnemyType.launcher.value

    def get_hp(self):
        return self.hp


# LookoutPoint
class LookoutPoint(Enemy):
    def __init__(self, location, soldier):
        super().__init__(location, 0)
        self.soldier = soldier

    # Getters
    @staticmethod
    def get_type():
        return Utility.EnemyType.lookout_point.value

    def get_soldier(self):
        return self.soldier

    def is_empty(self):
        if self.soldier is None:
            return True
        else:
            return False

    def set_soldier(self):
        self.soldier = None


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


# MoveApprovalMessage
class MoveApprovalMessage:
    # Constructor
    def __init__(self, field_object, location):
        self.field_object = field_object
        self.location = location

    # Getters
    def get_field_object(self):
        return self.field_object

    def get_move_to_location(self):
        return self.location


# EnemiesInSightMessage
class EnemiesInSightMessage:
    # Constructor
    def __init__(self, enemies):
        self.enemies = enemies

    # Getters
    def get_enemies(self):
        return self.enemies


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


# EngageApprovalMessage
class EngageApprovalMessage:
    # Constructor
    def __init__(self, company_num, field_object_id, enemy_id):
        self.company_num = company_num
        self.field_object_id = field_object_id
        self.enemy_id = enemy_id

    # Getters
    def get_company_num(self):
        return self.company_num

    def get_field_object_id(self):
        return self.field_object_id

    def get_enemy_id(self):
        return self.enemy_id


# GotShotMessage
class GotShotMessage:
    # Constructor
    def __init__(self, field_object):
        self.field_object = field_object

    def get_field_object(self):
        return self.field_object


# FieldUDP
class FieldUDP:
    # Constructor
    def __init__(self):
        self.logger = Utility.setup_logger('field', 'field.log')

        self.company1 = []
        self.company2 = []
        self.company3 = []

        self.forces = []

        self.enemies = []
        self.marked_enemies = []

        self.sock = Utility.get_field_sock()
        self.sock.bind(Utility.get_field_address())

        # Initiate and Start listen and report_location threads
        self.listen_thread = threading.Thread(target=self.listen)
        self.report_thread = threading.Thread(target=self.report_alive)
        self.check_for_enemies_thread = threading.Thread(target=self.check_for_enemies)
        self.enemies_check_for_forces_thread = threading.Thread(target=self.enemies_check_for_forces)
        self.enemy_attack_thread = threading.Thread(target=self.enemy_attack)

        self.listen_thread.start()
        self.report_thread.start()
        self.check_for_enemies_thread.start()
        self.enemies_check_for_forces_thread.start()
        self.enemy_attack_thread.start()

    # listen() - Listening to incoming packets on background, while receiving a packet, it goes to receive_handler()
    # func to handle the message.
    def listen(self):
        print('Listening...')
        self.logger.debug('Listening...')

        while True:
            # set max size of message
            rec_packet, rec_address = self.sock.recvfrom(65527)

            # decoding the message to String
            rec_packet = pickle.loads(rec_packet)
            if rec_packet:
                self.receive_handler(rec_packet, rec_address)

            # if STOP_FIELD_THREADS:
            #     logging.debug("Closing FieldUDP...")
            #     break

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
                    # if STOP_FIELD_THREADS:
                    #     break

                    if (((enemy.get_x() - field_object.get_x()) ** 2) +
                        ((enemy.get_y() - field_object.get_y()) ** 2)) < (forces_sight ** 2):
                        forces_in_sight.append(field_object)

                enemy.forces_in_sight(forces_in_sight)

    def get_enemy(self, enemy):
        for e in self.enemies:
            if e.get_id() == enemy.get_id():
                return e
        return None

    def forces_attack(self, field_object, enemy):
        print("got engage order")
        lookout_point_soldier = None
        field_object = self.get_field_object(field_object.get_company_num(), field_object.get_id())
        enemy = self.get_enemy(enemy)

        if enemy.get_type() == Utility.EnemyType.lookout_point.value:
            lookout_point_soldier = enemy.get_soldier()

        if field_object.get_type() == Utility.ObjectType.soldier.value:
            damage = random.randint(-2, 10)
        else:
            damage = random.randint(-3, 20)
        if damage < 0:
            damage = 0

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

                    if lookout_point_soldier is None:
                        field_object.shoot()
                        enemy.got_damage(damage)
                        print(enemy.get_hp())
                        if enemy.get_hp() <= 0:
                            field_object.attack_enemy(None)
                            self.enemies.remove(enemy)
                            break
                        time.sleep(1)
                    else:
                        field_object.shoot()
                        lookout_point_soldier.got_damage(damage)
                        print(lookout_point_soldier.get_hp())
                        if lookout_point_soldier.get_hp() <= 0:
                            field_object.attack_enemy(None)
                            enemy.set_soldier()
                            break
                        time.sleep(1)

            else:
                if field_object.get_move_to_location() is not None:
                    continue
                else:
                    location = enemy.get_location()
                    field_object.set_move_to(location)

                    move_to_thread = threading.Thread(target=self.move_to, args=(field_object, location[Utility.Location.X.value],
                                                                            location[Utility.Location.Y.value]))
                    move_to_thread.start()

                    while enemy not in field_object.get_in_sight():

                        if enemy is not field_object.get_attacking_enemy() or \
                                location is not field_object.get_move_to_location():
                            break
                        time.sleep(0.5)

    def enemy_attack(self):
        while True:
            for enemy in self.enemies:
                lookout_point_soldier = None
                if enemy.get_type() is Utility.EnemyType.lookout_point.value:
                    if enemy.is_empty():
                        continue
                    else:
                        lookout_point = enemy
                        enemy = lookout_point.get_soldier()

                if enemy.get_type() is Utility.EnemyType.launcher.value:
                    continue

                if (len(enemy.get_in_sight()) == 0 or enemy.get_ammo() <= 0) and lookout_point_soldier is None:
                    enemy.not_shooting()
                    continue
                elif (len(enemy.get_in_sight()) == 0 or enemy.get_ammo() <= 0) and lookout_point_soldier is not None:
                    lookout_point_soldier.not_shooting()
                    continue
                else:
                    damage = random.randint(-2, 10)
                    if damage < 0:
                        damage = 0

                    field_object = random.choice(enemy.get_in_sight())

                    if lookout_point_soldier is None:
                        enemy.shoot()
                    else:
                        lookout_point_soldier.shoot()
                    field_object.got_damage(damage)

                    if not field_object.is_got_shot():
                        field_object.got_shot_alert()
                        message = GotShotMessage(field_object)
                        packet = Packet(Utility.Sender.soldier.value, field_object.get_company_num(),
                                        Utility.Receiver.company_commander.value, Utility.MessageType.got_shot.value, message)
                        self.send_handler(packet)

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
        start_point = field_object.get_x(), field_object.get_y()
        end_point = float(new_x), float(new_y)
        while True:
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
                message = MoveApprovalMessage(field_object, location)
                send_packet = Packet(Utility.Sender.soldier.value, field_object.get_company_num(),
                                     Utility.Receiver.company_commander.value,
                                     Utility.MessageType.move_approval.value, message)
                self.send_handler(send_packet)
                self.logger.debug(
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

        # Error case
        else:
            # print(str(address) + " >> " + rec_packet)
            self.logger.error(str(address) + " >> " + str(rec_packet))

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
            self.logger.error("The message '{}' didn't reached to CC".format(send_packet))
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
