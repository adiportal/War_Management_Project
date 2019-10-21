import logging
import pickle
import threading
from Utility import Company, MessageType, Case, create_object_field, sender_receiver_switch_case, \
                    options_switch_case, get_sock, get_field_address, cc_main_menu, create_move_to_message, \
                    init_cc_address


# Initialize the Logger
logging.basicConfig(filename='CompanyCommanderLog.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : '
                                                                                    'CC : %(message)s')

# Initialize Companies
company1 = []
company2 = []
company3 = []

# Initialize Socket
sock = get_sock()


# listen() - Listening to incoming packets on background, while receiving a packet, it goes to receive_handler() func
#            to handle the message.
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


# receive_handler(packet, address) - Receive the packet and the address that it came from, check the case and act
#                                    according to the case
def receive_handler(packet, address):
    sender_receiver_case = sender_receiver_switch_case(packet)
    opt_case = options_switch_case(packet)
    message = packet.get_message()

    # Soldier >> CompanyCommander
    if sender_receiver_case == Case.soldier_to_cc.value:

        logging.debug("Received message from Soldier {} >> {}".format(address, packet))

        # New FieldObject message
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

        # Report Location message
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

        # change the packet approval to True and send it back to sender
        packet.set_approval(True)
        byte_packet = pickle.dumps(packet)
        sock.sendto(byte_packet, get_field_address())
        logging.debug("Approval packet has been sent: {}".format(packet))

    # Error Case
    else:
        logging.debug("Invalid Message:".format(packet))


# send_handler(packet) - if the CompanyCommander want to order on movement or engagement, after doing the action on
#                        the GUI, it create a packet and the packet goes to send_handler() to handle the message
def send_handler(packet):
    try:
        byte_packet = pickle.dumps(packet)
        sock.sendto(byte_packet, get_field_address())
        logging.debug("A Packet has been sent: {}".format(packet))
    except:
        logging.error("The packet '{}' didn't reached to Field {}".format(packet, get_field_address()))


# Main
def main():
    # Initialize Server Address
    cc_address = init_cc_address()

    # Bind the socket with the address
    sock.bind(cc_address)
    logging.info("A new socket has been initiated: {}".format(sock))

    # start listen() func on background
    listen_thread = threading.Thread(target=listen)
    listen_thread.start()
