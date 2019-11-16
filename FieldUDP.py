import sys
import logging
import threading
import time
import pickle

import Utility
from Entities import Packet, Soldier, BTW, AliveMessage
from Utility import Company, Sender, Receiver, MessageType, Case, Location, get_line, get_cc_address, \
                    sender_receiver_switch_case, options_switch_case, get_field_sock, get_field_address


# Initialize the Logger
logging.basicConfig(filename='FieldLog.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : '
                                                                         'Soldier : %(message)s')

# Initialize Companies
company1 = []
company2 = []
company3 = []


# Initialize Soldiers and BTWs
# Company 1
s1 = Soldier(1, (2, 4), 25)
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


# report_alive - A background function that reporting the status of the FieldObjects on the field status to their
#                CompanyCommanders every 2 seconds by moving the packet it creates to the send_handler() func
def report_alive():
    while True:
        for field_object in company1:
            message = AliveMessage(field_object)
            send_packet = Packet(Sender.soldier.value, field_object.get_company_num(), Receiver.company_commander.value,
                                 MessageType.alive.value, message)
            time.sleep(0.100)

            send_handler(send_packet)

        for field_object in company2:
            message = AliveMessage(field_object)
            send_packet = Packet(Sender.soldier.value, field_object.get_company_num(), Receiver.company_commander.value,
                                 MessageType.alive.value, message)
            time.sleep(0.100)

            send_handler(send_packet)

        for field_object in company3:
            message = AliveMessage(field_object)
            send_packet = Packet(Sender.soldier.value, field_object.get_company_num(), Receiver.company_commander.value,
                                 MessageType.alive.value, message)
            time.sleep(0.100)

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

    else:
        for field_object in company3:
            if field_object.get_id() == int(id):
                return field_object


# move_to(field_object, new_x, new_y) - while FieldUDP gets a MoveOrderMessage, the receive_handler() triggers the
#                                       move_to() func. it moves the FieldObject, step by step by it's own speed
def move_to(field_object, new_x, new_y):
    start = field_object.get_x(), field_object.get_y()
    end = float(new_x), float(new_y)

    steps = get_line(start, end)
    for step in steps:
        time.sleep(field_object.get_speed())
        step_x = step[Location.X.value]
        step_y = step[Location.Y.value]
        field_object.update_location(step_x, step_y)
    time.sleep(field_object.get_speed())
    field_object.update_location(new_x, new_y)


# receive_handler(packet, address) - Receive the packet and the address that it came from, check the case and act
#                                    according to the case
def receive_handler(rec_packet, address):
    case = sender_receiver_switch_case(rec_packet)

    # CompanyCommander >> Soldier
    if case == Case.cc_to_soldier.value:
        opt_case = options_switch_case(rec_packet)

        # Move Order message
        if opt_case == MessageType.move_order.value:
            message = rec_packet.get_message()
            location = message.get_new_location()
            new_x = location[Location.X.value]
            new_y = location[Location.Y.value]

            field_object = get_field_object(message.get_company_num(), message.get_field_object_id())

            move_to_thread = threading.Thread(target=move_to, args=(field_object, new_x, new_y))
            move_to_thread.start()

    # Error case
    else:
        print(str(address) + " >> " + rec_packet)
        logging.error(str(address) + " >> " + rec_packet)


# send_handler(send_packet) - Sending the packet that it gets
def send_handler(send_packet):
    cc_address = get_cc_address()
    try:
        byte_packet = pickle.dumps(send_packet)
        sock.sendto(byte_packet, cc_address)

    except:
        logging.error("The message '{}' didn't reached to CC".format(send_packet))
        print("The message '{}' did'nt reached to the Company Commander!!".format(send_packet))


# def init_field():
#     for field_object in company1:
#         message = AliveMessage(field_object)
#         packet = Packet(Sender.soldier.value,
#                         field_object.get_company_num(),
#                         Receiver.company_commander.value,
#                         MessageType.alive.value,
#                         message)
#
#         send_handler(packet)
#         time.sleep(0.100)
#
#     for field_object in company2:
#         message = AliveMessage(field_object)
#         packet = Packet(Sender.soldier.value,
#                         field_object.get_company_num(),
#                         Receiver.company_commander.value,
#                         MessageType.alive.value,
#                         message)
#
#         send_handler(packet)
#         time.sleep(0.100)


# **Main**
# Initiate Socket
sock = get_field_sock()

# Binding Socket
sock.bind(get_field_address())

# Initiate and Start listen and report_location threads
listen_thread = threading.Thread(target=listen)
report_thread = threading.Thread(target=report_alive)

listen_thread.start()
report_thread.start()


# sending all the FieldObjects
# init_field()


