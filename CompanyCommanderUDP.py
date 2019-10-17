import logging
import pickle
import threading
from Utility import Company, MessageType, Case, create_object_field, sender_receiver_switch_case, \
                    options_switch_case, get_sock, get_field_address, cc_main_menu, create_move_to_message, \
                    init_cc_address
from Entities import Packet

# Initialize the Logger
logging.basicConfig(filename='CompanyCommanderLog.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : '
                                                                                    'CC : %(message)s')

company1 = []
company2 = []
company3 = []

sock = get_sock()


def listen():
    print('Listening...\n')
    logging.debug("Listening...")

    while True:
        # set max size of message
        rec_packet, rec_address = sock.recvfrom(65527)

        # decoding the message to String
        rec_packet = pickle.loads(rec_packet)
        if rec_packet:
            receive_handler(rec_packet, get_field_address())


# def main_menu():
#     ans = ""
#     while ans == "":
#         ans = input(cc_main_menu())
#         if int(ans) != 1:
#             print("You can chose only 1 option for now")
#             ans = ""
#
#     company_num = ""
#     while company_num == "":
#         company_num = input("Enter company num: \n")
#         while not (1 <= int(company_num) <= 3):
#             company_num = input("You should Enter a number between 1-3: \n")
#
#     field_object_id = ""
#     contain = False
#     while field_object_id == "":
#         field_object_id = input("Enter FieldObject ID: \n")
#         for field_object in company1:
#             if field_object.get_id() == int(field_object_id):
#                 contain = True
#                 break
#         if not contain:
#             print("Company 1 does not contain an FieldObject #" + field_object_id)
#             field_object_id = ""
#
#     new_x = ""
#     while new_x == "":
#         new_x = input("Enter new X: \n")
#
#     new_y = ""
#     while new_y == "":
#         new_y = input("Enter new Y: \n")
#
#     new_location = float(new_x), float(new_y)
#
#     return create_move_to_message(company_num, field_object_id, new_location)


def receive_handler(packet, address):
    sender_receiver_case = sender_receiver_switch_case(packet)
    opt_case = options_switch_case(packet)
    message = packet.get_message()

    if sender_receiver_case == Case.soldier_to_cc.value:

        # printing the message and the client Address
        # print('Received message from Soldier {} >> {}'.format(address, packet))
        logging.debug("Received message from Soldier {} >> {}".format(address, packet))

        if opt_case == MessageType.new_field_object.value:
            new_object_field = create_object_field(message)
            logging.debug("New FieldObject was created: #{}".format(new_object_field.get_id()))

            company_num = new_object_field.get_company_num()

            if int(company_num) == Company.company1.value:
                company1.append(new_object_field)

            elif company_num == Company.company2.value:
                company2.append(new_object_field)

            else:
                company3.append(new_object_field)

            logging.debug("New FieldObject #{} from company {} was appended to company list".format
                          (new_object_field.get_id(), new_object_field.get_company_num()))

        if opt_case == MessageType.report_location.value:
            updated_object = message.get_field_object()

            if int(updated_object.get_company_num()) == Company.company1.value:
                updated = False
                for object_field in company1:
                    if object_field.get_id() == int(updated_object.get_id()):
                        object_field = updated_object
                        logging.debug("FieldObject #" + str(object_field.get_id()) + " location was updated to: (" +
                                      object_field.get_str_location() + ")")
                        updated = True
                        break

                if not updated:
                    logging.debug("Company 1 does not contain #" + str(updated_object.get_id()))

            elif int(updated_object.get_company_num()) == Company.company2.value:
                updated = False
                for object_field in company2:
                    if object_field.get_id() == int(updated_object.get_id()):
                        object_field = updated_object
                        logging.debug("#" + str(object_field.get_id()) + " location was updated to: " +
                                      object_field.get_str_location())
                        updated = True
                        break

                if not updated:
                    logging.debug("Company 2 does not contain #" + updated_object.get_id())

            else:
                updated = False
                for object_field in company3:
                    if object_field.get_id() == updated_object.get_id():
                        object_field = updated_object
                        logging.debug("#" + str(object_field.get_id()) + " location was updated to: " +
                                      object_field.get_str_location())
                        updated = True
                        break

                if not updated:
                    logging.debug("Company 3 does not contain #" + updated_object.get_id())

        packet.set_approval(True)
        byte_packet = pickle.dumps(packet)
        sock.sendto(byte_packet, get_field_address())
        logging.debug("Approval packet has been sent: {}".format(packet))

    # elif sender_receiver_case == 2:
    #
    #     logging.debug("Received message from Soldier {} : {}".format(address, msg))
    #     sock.sendto(msg.encode(), Utility.get_bc_address())
    #
    # elif sender_receiver_case == 3:
    #
    #     msg = msg[:-1]
    #
    #     logging.debug("Received message from BC {} : {}".format(address, msg))
    #     sock.sendto(msg.encode(), Utility.get_soldier_address())

    else:           # sender_receiver_case = 0
        logging.debug("Invalid Message:".format(packet))


def send_handler(packet):

    rec_msg = ''
    try:
        byte_packet = pickle.dumps(packet)
        sock.sendto(byte_packet, get_field_address())
        logging.debug("A Packet has been sent: {}".format(packet))

    except:
        logging.error("The packet '{}' didn't reached to Field {}".format(packet, get_field_address()))


def main():
    # Initialize Server Address
    cc_address = init_cc_address()

    # if cc_address == 0:  # 3 CompanyCommanders is open
    #     print("There are 3 Company Commanders already open in the system")
    #     quit()

    # Bind the socket with the address
    sock.bind(cc_address)
    logging.info("A new socket has been initiated: {}".format(sock))

    listen_thread = threading.Thread(target=listen)
    listen_thread.start()

    # if cc_address == 0:
    #     print("ERROR: INVALID Company Number")
    #     msg_str = ""
    #     continue
