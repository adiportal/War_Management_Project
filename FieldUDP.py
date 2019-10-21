import logging
import threading
from pyproj import _datadir, datadir
import time
import pickle
from Entities import Packet, UpdateFieldObjectMessage, Soldier, BTW
from Utility import MenuOptions, new_field_object_opt, Company, Sender, Receiver, MessageType, \
                    Case, Location, get_cc_address, soldier_main_menu, \
                    get_line, sender_receiver_switch_case, options_switch_case, get_sock, get_field_address


# Initialize the Logger
logging.basicConfig(filename='FieldLog.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : '
                                                                         'Soldier : %(message)s')

company1 = []
company2 = []
company3 = []

s1 = Soldier(1, (2, 4), 25)
s2 = Soldier(1, (2, 5), 25)
s3 = Soldier(1, (7, 3), 25)
s4 = Soldier(1, (9, 1), 25)
s5 = Soldier(1, (1, 4), 25)

btw1 = BTW(1, (2, 9), 50)
btw2 = BTW(1, (7, 1), 50)

company1 = [s1, s2, s3, s4, s5, btw1, btw2]


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


# def main_menu():
#     ans = ""
#     while ans == "":
#         ans = input(soldier_main_menu())
#         if int(ans) != MenuOptions.new_field_object.value:
#             print("You can chose only 1 option for now")
#             ans = ""
#
#         field_object = new_field_object_opt()
#
#         company_num = int(field_object.get_company_num())
#
#         if company_num == Company.company1.value:
#             company1.append(field_object)
#
#         elif company_num == Company.company2.value:
#             company2.append(field_object)
#
#         else:
#             company3.append(field_object)
#
#         send_packet = Packet(Sender.soldier.value,
#                              company_num,
#                              Receiver.company_commander.value,
#                              MessageType.new_field_object.value,
#                              field_object)
#         print(send_packet)
#         return send_packet


def report_location():
    while True:
        for field_object in company1:
            message = UpdateFieldObjectMessage(field_object)
            send_packet = Packet(Sender.soldier.value, field_object.get_company_num(), Receiver.company_commander.value,
                                 MessageType.report_location.value, message)

            send_handler(send_packet)
        time.sleep(2.0)


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


def receive_handler(rec_packet, address):
    case = sender_receiver_switch_case(rec_packet)

    if case == Case.approval.value:
        print("The Packet #{} Approved".format(rec_packet.get_id()))
        return

    elif case == Case.cc_to_soldier.value:
        opt_case = options_switch_case(rec_packet)

        if opt_case == MessageType.move_order.value:
            message = rec_packet.get_message()
            location = message.get_new_location()
            new_x = location[Location.X.value]
            new_y = location[Location.Y.value]

            field_object = get_field_object(message.get_company_num(), message.get_field_object_id())

            move_to_thread = threading.Thread(target=move_to, args=(field_object, new_x, new_y))
            move_to_thread.start()

    else:
        print(str(address) + " >> " + rec_packet)


# sendMassage
def send_handler(send_packet):

    rec_msg = ''
    try:
        byte_packet = pickle.dumps(send_packet)
        sock.sendto(byte_packet, cc_address)

    #     logging.debug("Message has been sent to CC {} : {}".format(cc_address, msg))
    #
    #     # rec_msg, cc_address = sock.recvfrom(65527)
    #     # rec_msg = rec_msg.decode('utf-8')
    #
    #     if case == Utility.Case.soldier_to_cc.value:
    #         # print receive message
    #         print("The message '{}' reached to Company Commander".format(rec_msg))
    #         logging.debug("The message '{}' reached to CC {}".format(rec_msg, cc_address))
    #
    #     elif case == Utility.Case.soldier_to_bc.value:
    #         print("The message '{}' reached to Battalion Commander".format(rec_msg))
    #         logging.debug("The message '{}' reached to BC {}".format(rec_msg, Utility.get_bc_address()))
    #
    #     else:
    #         logging.ERROR("An invalid message has reached: \'{}\'".format(rec_msg))
    #
    except:
        logging.error("The message '{}' didn't reached to CC".format(rec_msg))
        print("The message '{}' did'nt reached to the Company Commander!!".format(rec_msg))


# **Main**
sock = get_sock()
sock.bind(get_field_address())


listen_thread = threading.Thread(target=listen)
report_thread = threading.Thread(target=report_location)

listen_thread.start()
report_thread.start()

packet = ""

while packet == "":
    # packet = main_menu()

    cc_address = get_cc_address(1)

    if cc_address == 0:
        print("ERROR: INVALID Company Number")
        packet = ""
        continue

    for soldier in company1:
        packet = Packet(Sender.soldier.value,
                        soldier.get_company_num(),
                        Receiver.company_commander.value,
                        MessageType.new_field_object.value,
                        soldier)

        if packet != "":
            send_handler(packet)
        packet = ""
