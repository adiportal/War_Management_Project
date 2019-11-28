import logging
import pickle
import threading
from Utility import Company, MessageType, Case, sender_receiver_switch_case, get_field_address, contain, \
                    get_cc_listen_sock, get_cc_send_sock, get_cc_receive_address, get_cc_send_address
from Entities import CompanyCommander

# Initialize Companies
company1 = []
company2 = []
company3 = []

# Initialize Listen Socket
listen_sock = get_cc_listen_sock()

# Initialize Listen Socket
send_sock = get_cc_send_sock()

# Initiate CC
company_commander = CompanyCommander(1, (0, 0), 0)


# listen() - Listening to incoming packets on background, while receiving a packet, it goes to receive_handler() func
#            to handle the message.
def listen():
    print('Listening...\n')
    logging.debug("Listening...")

    while True:
        # set max size of message
        rec_packet, rec_address = listen_sock.recvfrom(65527)

        # decoding the message to String
        rec_packet = pickle.loads(rec_packet)
        if rec_packet:
            receive_handler(rec_packet, get_field_address())


# receive_handler(packet, address) - Receive the packet and the address that it came from, check the case and act
#                                    according to the case
def receive_handler(packet, address):
    sender_receiver_case = sender_receiver_switch_case(packet)
    opt_case = packet.get_message_type()
    message = packet.get_message()

    # Soldier >> CompanyCommander
    if sender_receiver_case == Case.soldier_to_cc.value:

        logging.debug("Received message from Soldier {} >> {}".format(address, packet))

        # New FieldObject message
        if opt_case == MessageType.alive.value:
            field_object = message.get_field_object()
            id = field_object.get_id()
            company_num = field_object.get_company_num()
            index = contain(get_company(company_num), id)

            if index >= 0:
                get_company(company_num)[index] = field_object
                logging.debug("FieldObject #{} was updated".format(id))
            else:
                get_company(company_num).append(field_object)
                logging.debug("New FieldObject was created: #{}".format(id))
                logging.debug("New FieldObject #{} from company {} was appended to company list".format(id,
                                                                                                        company_num))
        if opt_case == MessageType.enemies_in_sight.value:
            updated_enemies = message.get_enemies()
            company_commander.upldate_enemies(updated_enemies)

        if opt_case == MessageType.move_approval.value:
            field_object = message.get_field_object()
            id = field_object.get_id()
            location = message.get_move_to_location()
            logging.debug("FieldObject #{} start moving to ({})".format(id, location))

    # Error Case
    else:
        logging.debug("Invalid Message:".format(packet))


# send_handler(packet) - if the CompanyCommander want to order on movement or engagement, after doing the action on
#                        the GUI, it create a packet and the packet goes to send_handler() to handle the message
def send_handler(packet):
    try:
        byte_packet = pickle.dumps(packet)
        send_sock.sendto(byte_packet, get_field_address())
        logging.debug("A Packet has been sent: {}".format(packet))
    except:
        logging.error("The packet '{}' didn't reached to Field {}".format(packet, get_field_address()))


def set_company_commander(company_num, location):
    company_commander.set_company(company_num)
    company_commander.set_location(location)


# get_company(company_num) - get the company number and returns the list of FieldObject of this company number
def get_company(company_num):
    if company_num == Company.company1.value:
        return company1
    elif company_num == Company.company2.value:
        return company2
    else:
        return company3


# Main
def main(company_num, location):
    # Initialize the Logger
    logging.basicConfig(filename='CompanyCommanderLog.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : '
                                                                                        'CC : %(message)s')
    # Initialize receiver address
    cc_receiver_address = get_cc_receive_address()

    # Initialize sender address
    cc_sender_address = get_cc_send_address(company_num)

    # Bind the sockets with the addresses
    listen_sock.bind(cc_receiver_address)
    logging.info("A new socket has been initiated: {}".format(listen_sock))

    send_sock.bind(cc_sender_address)
    logging.info("A new socket has been initiated: {}".format(listen_sock))

    # Update CC
    set_company_commander(company_num, location)

    # start listen() func on background
    listen_thread = threading.Thread(target=listen)
    listen_thread.start()
