import logging
import pickle
import threading

from Entities import BattalionCommander
from Utility import Company, MessageType, Case, sender_receiver_switch_case, get_field_address, contain, \
    get_bc_listen_sock, get_cc_address, get_bc_address, get_bc_receive_address, setup_logger

# Initialize the Logger
logger = setup_logger('battalion_commander', 'battalion_commander.log')

global STOP_BC_THREADS
STOP_BC_THREADS = False

battalion_commander = BattalionCommander()

# Initialize Companies
company1 = []
company2 = []
company3 = []
enemies = []
company_commanders = []

# Initialize Listen Socket
listen_sock = get_bc_listen_sock()


# listen() - Listening to incoming packets on background, while receiving a packet, it goes to receive_handler() func
#            to handle the message.
def listen():
    print('Listening...\n')
    logger.debug("Listening...")

    while True:
        # set max size of message
        rec_packet, rec_address = listen_sock.recvfrom(65527)

        # decoding the message to String
        rec_packet = pickle.loads(rec_packet)
        # print(rec_packet)
        if rec_packet:
            receive_handler(rec_packet)

        if STOP_BC_THREADS:
            logger.debug("Closing BattalionCommanderUDP...")
            break


# receive_handler(packet, address) - Receive the packet and the address that it came from, check the case and act
#                                    according to the case
def receive_handler(packet):
    sender_receiver_case = sender_receiver_switch_case(packet)
    print(sender_receiver_case)
    opt_case = packet.get_message_type()
    message = packet.get_message()

    # Soldier >> CompanyCommander
    if sender_receiver_case == Case.soldier_to_cc.value:

        logger.debug("Received message from Soldier {}".format(packet))
        # New FieldObject message
        if opt_case == MessageType.alive.value:
            field_object = message.get_field_object()
            id = field_object.get_id()
            company_num = field_object.get_company_num()
            index = contain(get_company(company_num), id)

            if index >= 0:

                if field_object.get_hp() <= 0:
                    del get_company(company_num)[index]

                else:
                    get_company(company_num)[index] = field_object
                    logger.debug("FieldObject #{} was updated".format(id))
            else:
                get_company(company_num).append(field_object)
                logger.debug("New FieldObject was created: #{}".format(id))
                logger.debug("New FieldObject #{} from company {} was appended to company list".format(id,
                                                                                                        company_num))

        elif opt_case == MessageType.move_approval.value:
            field_object = message.get_field_object()
            id = field_object.get_id()
            location = message.get_move_to_location()
            logger.debug("FieldObject #{} start moving to ({})".format(id, location))

        elif opt_case == MessageType.got_shot.value:
            field_object = message.get_field_object()
            id = field_object.get_id()

            print("#{} Got Shot!!".format(id))
            logger.debug("#{} Got Shot!!".format(id))

        elif opt_case == MessageType.enemies_in_sight.value:

            updated_enemies = message.get_enemies()
            battalion_commander.update_enemies(updated_enemies)

    elif sender_receiver_case == Case.cc_to_bc.value:
        # if opt_case == MessageType.alive.value:
        cc = message.get_field_object()
        battalion_commander.commanders.append(cc)
        print(len(battalion_commander.commanders))

    # Error Case
    else:
        logger.debug("Invalid Message:".format(packet))


# get_company(company_num) - get the company number and returns the list of FieldObject of this company number
def get_company(company_num):
    if company_num == Company.company1.value:
        return company1
    elif company_num == Company.company2.value:
        return company2
    else:
        return company3


# Main
def main():
    # Initialize receiver address
    bc_receiver_address = get_bc_receive_address()

    # Bind the sockets with the addresses
    listen_sock.bind(bc_receiver_address)
    logger.info("A new socket has been initiated: {}".format(listen_sock))

    # start listen() func on background
    listen_thread = threading.Thread(target=listen)
    listen_thread.start()
