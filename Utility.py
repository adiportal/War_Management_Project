import socket
import enum
import logging
import Entities
from pyproj import Geod
from Entities import Soldier, BTW, InitMessage

logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Utility : %(message)s')


def get_sock():
    # Initialize socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    return sock


def get_soldier_address():
    IP = '127.0.0.1'
    port = 5001
    return IP, port


# get Soldier Address
def init_cc_address():
    IP = '127.0.0.1'
    port = 5004
    count = 0

    while not is_open(IP, port) and count != 3:
        port += 1
        count += 1

    if count == 3:
        return Case.error

    return (IP, port)


# get Company Commander Address
def get_cc_address(company_num):
    IP = '127.0.0.1'
    if int(company_num) == Company.company1.value:
        port = 5004

        if not is_open(IP, port):
            return IP, port
        else:
            return Case.error.value

    elif int(company_num) == Company.company2.value:
        port = 5005

        if not is_open(IP, port):
            return IP, port
        else:
            return Case.error.value

    elif int(company_num) == Company.company3.value:
        port = 5006

        if not is_open(IP, port):
            return IP, port
        else:
            return Case.error.value

    else:
        return Case.error.value


def get_bc_address():
    IP = '127.0.0.1'
    port = 5003
    return (IP, port)


def company_num_by_port(port):
    if port == 5004:
        return 1
    elif port == 5005:
        return 2
    elif port == 5006:
        return 3
    else:
        return Case.error.value


# get Battalion Commander Address
def sender_receiver_switch_case(msg_str):

    if msg_str[0] == "*":
        return Case.approval.value

    msg_list = msg_str.split(" :: ")

    # sender = Soldier, receiver = CC
    if int(msg_list[FullMessageIndexes.sender.value]) == Sender.soldier.value and \
       int(msg_list[FullMessageIndexes.receiver.value]) == Receiver.company_commander.value:
        return Case.soldier_to_cc.value

    # sender = Soldier, receiver = BC
    elif int(msg_list[FullMessageIndexes.sender.value]) == Sender.soldier.value and \
            int(msg_list[FullMessageIndexes.receiver.value]) == Receiver.battalion_commander.value and \
            msg_str[-1] != "*":
        return Case.soldier_to_bc.value

    # sender = BC, receiver = CC -> Soldier
    elif int(msg_list[FullMessageIndexes.sender.value]) == Sender.soldier.value and \
            int(msg_list[FullMessageIndexes.receiver.value]) == Receiver.battalion_commander.value and msg_str[-1] == "*":
        return Case.bc_to_cc_approval.value

    # sender = CC, receiver = soldier
    elif int(msg_list[FullMessageIndexes.sender.value]) == Sender.company_commander.value and \
            int(msg_list[FullMessageIndexes.receiver.value]) == Receiver.soldier.value:
        return Case.cc_to_soldier.value

    else:
        return Case.error.value


def options_switch_case(msg):
    msg_list = msg.split(" :: ")

    if int(msg_list[FullMessageIndexes.message_type.value]) == MessageType.update_location.value:
        return 1

    elif int(msg_list[FullMessageIndexes.message_type.value]) == MessageType.move_order.value:
        return 2

    elif int(msg_list[FullMessageIndexes.message_type.value]) == MessageType.engage_order.value:
        return 3

    elif int(msg_list[FullMessageIndexes.message_type.value]) == MessageType.new_field_object.value:
        return 4

    elif int(msg_list[FullMessageIndexes.message_type.value]) == MessageType.report_location.value:
        return 5

    else:   # Error
        return 0


# Check Message
def is_open(IP, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((IP, port))
        result = True
    except:
        result = False
    sock.close()
    return result


def soldier_main_menu():
    return "Choose your option:\n" \
           "(1)     Initiate a new FieldObject \n"


def cc_main_menu():
    return "Choose your option:\n" \
           "(1)     Move FieldObject \n"


def new_field_object_opt():

    object_type = ""
    while object_type == "":
        object_type = input("Enter FieldObject type: \n"
                            "(1)     Soldier \n"
                            "(2)     BTW \n")
        if not (1 <= int(object_type) <= 2):
            print("You should Enter a number (1-2)")
            object_type = ""

    company_num = ""
    while company_num == "":
        company_num = input("Enter Company number (1-3): ")
        if not (1 <= int(company_num) <= 3):
            print("You should Enter a number (1-3)")
            company_num = ""

    x = ""
    y = ""
    while x == "":
        x = input("Enter Location: \n"
                  "Enter X: ")

        y = input("Enter Y: ")

    location = [x, y]

    ammo = ""
    while ammo == "":
        ammo = input("Enter Ammo amount: ")
        if not int(ammo) >= 0:
            print("You should enter a number greater then 0: ")
            ammo = ""

    if object_type == ObjectType.soldier.value:
        field_object = Soldier(company_num, location, ammo)
    else:
        field_object = BTW(company_num, location, ammo)

    obj_and_msg = field_object, InitMessage(field_object)
    return obj_and_msg


# def create_init_message(field_object):
#     message = field_object[ObjectListIndex.object_type.value] + " ; " + \
#               field_object[ObjectListIndex.company_num.value] + " ; " + \
#               (field_object[ObjectListIndex.location.value])[Location.X.value] + "," + \
#               (field_object[ObjectListIndex.location.value])[Location.Y.value] + " ; " + \
#               field_object[ObjectListIndex.ammo.value]
#     return message


# def create_object_field(msg):
#     object_list = msg.split(" ; ")
#     location_str = object_list[ObjectListIndex.location.value]
#     location_list = location_str.split(",")
#
#     if object_list[ObjectListIndex.object_type.value] == str(ObjectType.soldier.value):
#         soldier = Entities.Soldier(int(object_list[ObjectListIndex.company_num.value]),
#                                    (float(location_list[Location.X.value]),
#                                    float(location_list[Location.Y.value])),
#                                    int(object_list[ObjectListIndex.ammo.value]))
#
#         return soldier
#
#     else:
#         btw = Entities.BTW(int(object_list[ObjectListIndex.company_num.value]),
#                            (float(location_list[Location.X.value]),
#                            float(location_list[Location.Y.value])),
#                            int(object_list[ObjectListIndex.ammo.value]))
#
#         return btw


def create_move_to_message(company_num, field_object_id, new_location):

    message = str(Sender.company_commander.value) + " :: " + \
              company_num + " :: " + \
              str(Receiver.soldier.value) + " :: " + \
              str(MessageType.move_order.value) + " :: " + \
              company_num + " ; " + \
              field_object_id + " ; " + new_location

    return message


def get_line(start, end):
    x1 = start[Location.X.value]
    y1 = start[Location.Y.value]

    x2 = end[Location.X.value]
    y2 = end[Location.Y.value]

    geod = Geod("+ellps=WGS84")
    points = geod.npts(x1, y1,
                       x2, y2,
                       npts=100)

    return points


# Enum Classes
class Sender(enum.Enum):
    soldier = 1
    company_commander = 2
    battalion_commander = 3


class Receiver(enum.Enum):
    soldier = 1
    company_commander = 2
    battalion_commander = 3


class Company(enum.Enum):
    company1 = 1
    company2 = 2
    company3 = 3


class Case(enum.Enum):
    soldier_to_cc = 1
    soldier_to_bc = 2
    bc_to_cc_approval = 3
    cc_to_soldier = 4
    approval = 5
    error = 0


class ObjectType(enum.Enum):
    soldier = 1
    btw = 2


class FullMessageIndexes(enum.Enum):    # sender.company_num.receiver.message_type.message
    sender = 0
    company_num = 1
    receiver = 2
    message_type = 3
    message = 4


class MessageType(enum.Enum):
    update_location = 1
    move_order = 2
    engage_order = 3
    new_field_object = 4
    report_location = 5


class ObjectListIndex(enum.Enum):
    object_type = 0
    company_num = 1
    location = 2
    ammo = 3


class Location(enum.Enum):
    X = 0
    Y = 1


class ListAndMsg(enum.Enum):
    list = 0
    msg = 1


class MenuOptions(enum.Enum):
    new_field_object = 1
    field_object_location = 2


class ReportMessageIndexes(enum.Enum):
    company_num = 0
    id = 1
    location = 2


class MoveToMessageIndexes(enum.Enum):
    company_num = 0
    field_object_id = 1
    location = 2

