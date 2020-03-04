from datetime import datetime
import pickle
import threading
import time

import Utility
from Utility import Company, MessageType, Case, sender_receiver_switch_case, get_field_address, contain, \
    get_cc_listen_sock, get_cc_send_sock, get_cc_receive_address, get_cc_send_address, Sender, Receiver, setup_logger, \
    get_cc_to_bc_send_sock, get_bc_address, get_cc_to_bc_send_address
from Entities import CompanyCommander, AliveMessage, Packet, NotApprovedMessage, CompanyCommanderScenario, Message

# Initialize the Logger
# logging.basicConfig(filename='CompanyCommanderLog.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : '
#                                                                                     'CC : %(message)s')
logger = setup_logger('company_commander', 'company_commander.log')

# Initialize Companies
company1 = []
company2 = []
company3 = []

# Order Packets
order_packets = []

# Console Messages
console_messages = []

# Initialize Listen Socket
listen_sock = get_cc_listen_sock()

# Initialize Send Socket
send_sock = get_cc_send_sock()

# Initialize cc to bc Send Socket
cc_to_bc_sock = get_cc_to_bc_send_sock()

# Initiate CC
company_commander = CompanyCommander(1, (0, 0), 0)

date_t = datetime.now().strftime("%d-%m-%Y %H.%M.%S")
scenario = CompanyCommanderScenario()


def get_company_commander():
    return company_commander


# listen() - Listening to incoming packets on background, while receiving a packet, it goes to receive_handler() func
#            to handle the message.
def listen():
    print('Listening... \n')
    logger.debug("Listening...")

    while True:
        # set max size of message
        rec_packet, rec_address = listen_sock.recvfrom(65527)

        # decoding the message to String
        rec_packet = pickle.loads(rec_packet)
        if rec_packet:
            receive_handler(rec_packet, get_field_address())

        if company_commander.is_stopped():
            logger.debug("Closing CompanyCommanderUDP...")
            print("Closing CompanyCommanderUDP...")
            break


# receive_handler(packet, address) - Receive the packet and the address that it came from, check the case and act
#                                    according to the case
def receive_handler(packet, address):
    sender_receiver_case = sender_receiver_switch_case(packet)
    opt_case = packet.get_message_type()
    message = packet.get_message()

    # Soldier >> CompanyCommander
    if sender_receiver_case == Case.soldier_to_cc.value:

        logger.debug("Received message from Soldier {} >> {}".format(address, packet))

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
        elif opt_case == MessageType.enemies_in_sight.value:
            updated_enemies = message.get_enemies()
            company_commander.update_enemies(updated_enemies)

        elif opt_case == MessageType.move_approval.value:
            for pac in order_packets:
                if message.get_approval_packet_id() == pac.get_id():
                    order_packets.remove(pac)
                    now = datetime.now()
                    dt_string = now.strftime("%H:%M:%S")
                    console_messages.append(
                        ("[ " + dt_string + " ]" + "  " + f"#{message.get_field_object().get_id()} started moving <br />",
                         Utility.MessageType.move_approval.value))
                    break

            field_object = message.get_field_object()
            id = field_object.get_id()
            location = message.get_move_to_location()
            logger.debug("FieldObject #{} start moving to ({})".format(id, location))

        elif opt_case == MessageType.engage_approval.value:
            for pac in order_packets:
                if message.get_approval_packet_id() == pac.get_id():
                    order_packets.remove(pac)
                    now = datetime.now()
                    dt_string = now.strftime("%H:%M:%S")
                    console_messages.append(
                        ("[ " + dt_string + " ]" + "  " + f"#{message.get_field_object_id()} started engaging "
                                                        f"target <br />",
                         Utility.MessageType.engage_approval.value))
                    break

            field_object = message.get_field_object_id()
            logger.debug(f"FieldObject #{field_object} Engaging Enemy")

        elif opt_case == MessageType.got_shot.value:
            field_object = message.get_field_object()
            id = field_object.get_id()

            print("#{} Got Shot!!".format(id))
            logger.debug("#{} Got Shot!!".format(id))
            if field_object.get_company_num() == company_commander.get_company_num():
                now = datetime.now()
                dt_string = now.strftime("%H:%M:%S")
                console_messages.append(
                    ("[ " + dt_string + " ]" + " " + f"#{id} got shot <br />", Utility.MessageType.got_shot.value))

    # Error Case
    else:
        logger.debug("Invalid Message:".format(packet))


# send_handler(packet) - if the CompanyCommander want to order on movement or engagement, after doing the action on
#                        the GUI, it create a packet and the packet goes to send_handler() to handle the message
def send_handler(packet):
    try:
        if sender_receiver_switch_case(packet) == Case.cc_to_bc.value:
            address = get_bc_address()
            sock = cc_to_bc_sock
        else:
            address = get_field_address()
            sock = send_sock

        byte_packet = pickle.dumps(packet)
        message = packet.get_message()

        if packet.get_message_type() == MessageType.move_order.value or \
                packet.get_message_type() == MessageType.engage_order.value:

            message_type = None
            field_object_id = None

            if packet.get_message_type() == MessageType.move_order.value:
                message_type = "Move Order"
                field_object_id = message.get_field_object_id()
            else:
                message_type = "Engage Order"
                field_object_id = message.get_field_object().get_id()

            order_packets.append(packet)
            count = 0

            while packet in order_packets:
                if count == 3:
                    order_packets.remove(packet)
                    now = datetime.now()
                    dt_string = now.strftime("%H:%M:%S")
                    console_messages.append(
                        ("[ " + dt_string + " ]" + "  " + f"Soldier #{field_object_id} didn't approved the {message_type} <br />",
                         Utility.MessageType.not_approved_message.value))

                    message = NotApprovedMessage(field_object_id, company_commander.get_company_num())
                    msg = Message(datetime.now().strftime("%H:%M:%S"), message)
                    scenario.save_message(msg)

                    logger.error("The packet '{}' didn't reached to Field {}".format(packet, get_field_address()))
                    break

                sock.sendto(byte_packet, address)
                logger.debug("A Packet has been sent: {}".format(packet))
                msg = Message(datetime.now().strftime("%H:%M:%S"), message)
                scenario.save_message(msg)

                count += 1
                time.sleep(3)

        else:
            sock.sendto(byte_packet, address)
            logger.debug("A Packet has been sent: {}".format(packet))

            # msg = Message(datetime.now().strftime("%H:%M:%S"), message)
            # scenario.save_message(msg)

    except:
        logger.error("The packet '{}' didn't reached to Field {}".format(packet, get_field_address()))


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


def report_alive():
    while True:
        message = AliveMessage(company_commander)
        send_packet = Packet(Sender.company_commander.value, company_commander.get_company_num(),
                             Receiver.battalion_commander.value, MessageType.alive.value, message)

        send_handler(send_packet)
        time.sleep(10)


def set_scenario():
    date_time = datetime.now().strftime("%d-%m-%Y %H.%M.%S")
    scenario.set_file_name(f"CompanyCommander{company_commander.get_company_num()}Scenario {date_time}")
    scenario.set_date_time(date_time)
    scenario.set_company_num(company_commander.get_company_num())
    scenario.set_company_commander(company_commander)


# Main
def main(company_num, location):
    # # Initialize the Logger
    # logging.basicConfig(filename='CompanyCommanderLog.log', level=logging.DEBUG, format='%(asctime)s :
    # %(levelname)s : '
    #                                                                                     'CC : %(message)s')
    # Initialize receiver address
    cc_receiver_address = get_cc_receive_address()

    # Initialize sender address
    cc_sender_address = get_cc_send_address(company_num)

    # Initialize cc to bc send address
    cc_to_bc_address = get_cc_to_bc_send_address(company_num)

    # Bind the sockets with the addresses
    listen_sock.bind(cc_receiver_address)
    logger.info("A new socket has been initiated: {}".format(listen_sock))

    send_sock.bind(cc_sender_address)
    logger.info("A new socket has been initiated: {}".format(send_sock))

    cc_to_bc_sock.bind(cc_to_bc_address)
    logger.info("A new socket has been initiated: {}".format(cc_to_bc_sock))

    # Update CC
    set_company_commander(company_num, location)

    date_time = datetime.now().strftime("%d-%m-%Y.%H.%M.%S")
    scenario.set_file_name(f"CompanyCommander{company_commander.get_company_num()}Scenario.{date_time}")
    scenario.set_date_time(date_time)
    scenario.set_company_num(company_commander.get_company_num())
    scenario.set_company_commander(company_commander)

    # start listen() func on background
    listen_thread = threading.Thread(target=listen)
    alive_thread = threading.Thread(target=report_alive)

    listen_thread.start()
    alive_thread.start()

    # time.sleep(10)
    # packet = Utility.create_move_to_message(company1[0].get_company_num(), company1[0].get_id(), (5, 6))
    # send_handler(packet)
