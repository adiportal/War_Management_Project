import logging
import threading

import Utility

# Initialize the Logger
logging.basicConfig(filename='CompanyCommander.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : CC : %(message)s')

company1 = []
company2 = []
company3 = []

def listen():
    print('Listening...\n')

    while True:
        # set max size of message
        rec_msg, rec_address = sock.recvfrom(65527)

        # decoding the message to String
        rec_msg = rec_msg.decode('utf-8')
        if rec_msg:
            receive_handler(rec_msg, rec_address)


def receive_handler(msg, address):
    case = Utility.switch_case(msg)
    full_msg_list = msg.split(" :: ")
    msg_str = full_msg_list[Utility.MessageIndexes.message_type.value]
    msg_list = msg_str.split(" ; ")
    print(str(msg_list))

    if case == Utility.Case.soldier_to_cc.value:

        # printing the message and the client Address
        print('Received message from Soldier {} >> {}'.format(address, msg))
        logging.debug("Received message from Soldier {} >> {}".format(address, msg))

        if int(msg_list[Utility.ObjectType.soldier.value]) == int(Utility.ObjectType.soldier.value):
            new_object_field = Utility.create_object_field(msg_str)
            print(new_object_field)
            company1.append(new_object_field)

        msg = "*" + msg
        sock.sendto(msg.encode(), Utility.get_soldier_address())

    # elif case == 2:
    #
    #     logging.debug("Received message from Soldier {} : {}".format(address, msg))
    #     sock.sendto(msg.encode(), Utility.get_bc_address())
    #
    # elif case == 3:
    #
    #     msg = msg[:-1]
    #
    #     logging.debug("Received message from BC {} : {}".format(address, msg))
    #     sock.sendto(msg.encode(), Utility.get_soldier_address())

    else:           # case = 0
        logging.ERROR("An invalid message has reached: \'{}\'".format(msg))


def send_handler(msg, sock, cc_address):

    case = Utility.switch_case(msg)
    rec_msg = ''
    try:
        sock.sendto(msg.encode(), cc_address)

    except:
        logging.error("The message '{}' didn't reached to CC {}".format(rec_msg, cc_address))
        print("The message '{}' did'nt reached to the Company Commander!!".format(rec_msg))


# Main
# Initialize Server Address
cc_address = Utility.init_cc_address()

if cc_address == 0:   # 3 CompanyCommanders is open
    print("There are 3 Company Commanders already open in the system")
    quit()

sock = Utility.get_sock()


# Bind the socket with the address
sock.bind(cc_address)
logging.info(sock)

listen_thread = threading.Thread(target=listen)
listen_thread.start()

msg_str = ""

while msg_str == "":
    msg_str = input("Write your message: ")

    cc_address = ("127.0.0.1", 5002)

    # if cc_address == 0:
    #     print("ERROR: INVALID Company Number")
    #     msg_str = ""
    #     continue

    if msg_str != "":
        send_handler(msg_str, sock, cc_address)
        print("done")
    msg_str = ""