import socket
import enum
import logging
import Entities
from pyproj import Geod

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
def switch_case(msg_str):

    if msg_str[0] == "*":
        return Case.approval.value

    msg_list = msg_str.split(".")

    # sender = Soldier, receiver = CC
    if int(msg_list[MessageIndexes.sender.value]) == Sender.soldier.value and \
            int(msg_list[MessageIndexes.receiver.value]) == Receiver.company_commander.value:
        return Case.soldier_to_cc.value

    # sender = Soldier, receiver = BC
    elif int(msg_list[MessageIndexes.sender.value]) == Sender.soldier.value and \
            int(msg_list[MessageIndexes.receiver.value]) == Receiver.battalion_commander.value and \
            msg_str[-1] != "*":
        return Case.soldier_to_bc.value

    # sender = BC, receiver = CC -> Soldier
    elif int(msg_list[MessageIndexes.sender.value]) == Sender.soldier.value and \
            int(msg_list[MessageIndexes.receiver.value]) == Receiver.battalion_commander.value and msg_str[-1] == "*":
        return Case.bc_to_cc_approval.value

    # sender = CC, receiver = soldier
    elif int(msg_list[MessageIndexes.sender.value]) == Sender.company_commander.value and \
            int(msg_list[MessageIndexes.receiver.value]) == Receiver.soldier.value:
        return Case.cc_to_soldier.value

    else:
        return Case.error.value


# Check Message                     MSG ICD: Sender.Receiver.MSG (str)
def is_open(IP, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((IP, port))
        result = True
    except:
        result = False
    sock.close()
    return result


def main_menu():
    return "Choose your option:\n" \
           "(1)     Initiate a new FieldObject \n" \
           "(2)     Send FieldObject location \n"


def new_field_object_opt():
    object_list = []

    object_type = ""
    while object_type == "":
        object_type = input("Enter FieldObject type: \n"
                            "(1)     Soldier \n"
                            "(2)     BTW \n")
        if not (1 <= int(object_type) <= 2):
            print("You should Enter a number (1-2)")
            object_type = ""

    object_list.append(object_type)

    company_num = ""
    while company_num == "":
        company_num = input("Enter Company number (1-3): ")
        if not (1 <= int(company_num) <= 3):
            print("You should Enter a number (1-3)")
            company_num = ""

    object_list.append(company_num)

    x = ""
    y = ""
    while x == "":
        x = input("Enter Location: \n"
                  "Enter X: ")

        y = input("Enter Y: ")

    location = [x, y]

    object_list.append(location)

    ammo = ""
    while ammo == "":
        ammo = input("Enter Ammo amount: ")
        if not int(ammo) >= 0:
            print("You should enter a number greater then 0: ")
            ammo = ""

        object_list.append(ammo)

    return object_list


def create_init_message(object_list):
    message = "1.2." + object_list[ObjectListIndex.object_type.value] + "." \
                     + object_list[ObjectListIndex.company_num.value] + "."\
                     + (object_list[ObjectListIndex.location.value])[Location.X.value] + "," \
                     + (object_list[ObjectListIndex.location.value])[Location.Y.value] + "." \
                     + object_list[ObjectListIndex.ammo.value]
    print(message)
    return message


def create_object_field(object_list):
    if int(object_list[ObjectListIndex.object_type.value]) == int(ObjectType.soldier.value):
        soldier = Entities.Soldier(int(object_list[ObjectListIndex.company_num.value]),
                                   (float((object_list[ObjectListIndex.location.value])[Location.X.value]),
                                   float((object_list[ObjectListIndex.location.value])[Location.Y.value])),
                                   int(object_list[ObjectListIndex.ammo.value]))

        return soldier

    else:
        btw = Entities.BTW(int(object_list[ObjectListIndex.company_num.value]),
                           (int((object_list[ObjectListIndex.location.value])[Location.X.value]),
                            int((object_list[ObjectListIndex.location.value])[Location.Y.value])),
                           int(object_list[ObjectListIndex.ammo.value]))

        return btw


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


class MessageIndexes(enum.Enum):    # sender.company_num.receiver.message_type.message 1.2.1.hello
    sender = 0
    company_num = 1
    receiver = 2
    message_type = 3
    message = 4


class MessageType(enum.Enum):
    update_location = 1
    move_order = 2
    engage_order = 3
    initiate_soldier = 4


class ObjectListIndex(enum.Enum):
    object_type = 0
    company_num = 1
    location = 2
    ammo = 3


class Location(enum.Enum):
    X = 0
    Y = 1


class MessageType(enum.Enum):
    location_reporting = 1
    object_field_init = 2

