import socket
import enum
import logging
from pyproj import Geod
import Entities


# Initialize the Logger
logging.basicConfig(filename='UtilityLog.log', level=logging.DEBUG,
                    format='%(asctime)s : %(levelname)s : Utility : %(message)s')


# get_cc_sock() - creating a new socket for cc and returns it
def get_cc_sock():
    # Initialize socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    return sock


# get_field_sock() - creating a new socket for field and returns it
def get_field_sock():
    # Initialize socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    return sock


# Getters
def get_field_address():
    IP = '127.0.0.1'
    port = 5001
    return IP, port


def get_cc_address(company_num):
    IP = '255.255.255.255'

    if int(company_num) == Company.company1.value:
        port = 5004
        return IP, port

    elif int(company_num) == Company.company2.value:
        port = 5005
        return IP, port

    elif int(company_num) == Company.company3.value:
        port = 5006
        return IP, port

    else:
        return Case.error.value


def init_cc_address(company_num):
    IP = ''

    if int(company_num) == Company.company1.value:
        port = 5004
        return IP, port

    elif int(company_num) == Company.company2.value:
        port = 5005
        return IP, port

    elif int(company_num) == Company.company3.value:
        port = 5006
        return IP, port

    else:
        return Case.error.value


def get_bc_address():
    IP = '127.0.0.1'
    port = 5003
    return IP, port


def company_num_by_port(port):
    if port == 5004:
        return 1
    elif port == 5005:
        return 2
    elif port == 5006:
        return 3
    else:
        return Case.error.value


# sender_receiver_case(packet) - get the packet and returns the case of sender-receiver
def sender_receiver_switch_case(packet):

    if packet.is_approved():
        return Case.approval.value

    # sender = Soldier, receiver = CC
    if packet.get_sender() == Sender.soldier.value and \
       packet.get_receiver() == Receiver.company_commander.value:
        return Case.soldier_to_cc.value

    # sender = Soldier, receiver = BC
    elif packet.get_sender() == Sender.soldier.value and \
            packet.get_receiver() == Receiver.battalion_commander.value and \
            not packet.is_bc_approved():
        return Case.soldier_to_bc.value

    # sender = BC, receiver = CC -> Soldier
    elif packet.get_sender() == Sender.soldier.value and \
            packet.get_receiver() == Receiver.battalion_commander.value and \
            packet.is_bc_approved():
        return Case.bc_to_cc_approval.value

    # sender = CC, receiver = soldier
    elif packet.get_sender() == Sender.company_commander.value and \
            packet.get_receiver() == Receiver.soldier.value:
        return Case.cc_to_soldier.value

    else:
        return Case.error.value


# option_switch_case(packet) - return the case according to the packet MessageType
def options_switch_case(packet):

    if packet.get_message_type() == MessageType.alive.value:
        return 1

    elif packet.get_message_type() == MessageType.move_order.value:
        return 2

    elif packet.get_message_type() == MessageType.engage_order.value:
        return 3

    else:   # Error
        return 0


# in_use(IP, port) - return a boolean variable that tells if address (IP, port) is in use. True = already open
#                                                                                           False = free to use
def in_use(address):
    IP = address[0]
    port = address[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((IP, port))
        result = False
    except:
        result = True
    sock.close()
    return result


# create_move_to_message(company_num, field_object_id, new_location) - create a MoveOrderMessage and Packet and returns
#                                                                      the Packet
def create_move_to_message(company_num, field_object_id, new_location):

    message = Entities.MoveOrderMessage(company_num, field_object_id, new_location)
    packet = Entities.Packet(Sender.company_commander.value, company_num, Receiver.soldier.value,
                             MessageType.move_order.value, message)

    return packet


# contain(company, id) - check if FieldObject is in company list by ID. If the searched FieldObject is in the list,
#                        it returns the index of the object. else, it returns -1.
def contain(company, id):
    count = 0
    for field_object in company:
        if field_object.get_id() == id:
            return count
        else:
            count += 1
    return -1


# get_line(start, end) - get a start and end points and return a list of lined steps
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
# Cases
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
    alive = 1
    move_order = 2
    engage_order = 3


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


class ReportMessageIndexes(enum.Enum):
    company_num = 0
    id = 1
    location = 2

class MoveToMessageIndexes(enum.Enum):
    company_num = 0
    field_object_id = 1
    location = 2
