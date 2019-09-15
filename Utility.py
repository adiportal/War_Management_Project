import logging
import socket

logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Utility : %(message)s')


# getSock
def get_sock():
    # Initialize socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    return sock


# get Soldier Address
def get_soldier_address():
    IP = '127.0.0.1'
    port = 5001
    return (IP, port)


# get Company Commander Address
def init_cc_address():
    IP = '127.0.0.1'
    port = 5004
    count = 0

    while is_open(IP, port) == False and count != 3:
        port += 1
        count += 1

    if count == 3:
        return 0

    return (IP, port)

def init_bc_address():
    IP = '127.0.0.1'
    port = 5003
    count = 0

    while is_open(IP, port) == False and count != 1:
        port += 1
        count += 1

    if count == 1:
        return 0

    return (IP, port)

def init_soldier_address():
    IP = '127.0.0.1'
    port = 5001
    count = 0

    while is_open(IP, port) == False and count != 1:
        port += 1
        count += 1

    if count == 1:
        return 0

    return (IP, port)

def get_cc_address(company_num):
    IP = '127.0.0.1'

    if int(company_num) == 1:
        port = 5004

        if is_open(IP, port) == False:
            return (IP, port)
        else:
            return 0

    elif int(company_num) == 2:
        port = 5005

        if is_open(IP, port) == False:
            return (IP, port)
        else:
            return 0

    elif int(company_num) == 3:
        port = 5006

        if is_open(IP, port) == False:
            return (IP, port)
        else:
            return 0

    else:
        return 0

# get Battalion Commander Address
def get_bc_address():
    IP = '127.0.0.1'
    port = 5003
    return (IP, port)


# Check Message                     MSG ICD: Sender.Receiver.MSG (str)
def switch_case(msg_str):

    msg_list = split_message(msg_str)

    # sender = Soldier, receiver = CC
    if int(msg_list[0]) == 1 and int(msg_list[2]) == 2:
        return 1

    # sender = Soldier, receiver = BC
    elif int(msg_list[0]) == 1 and int(msg_list[2]) == 3 and msg_str[-1] != "*":
        return 2

    # sender = BC, receiver = CC -> Soldier
    elif int(msg_list[0]) == 1 and int(msg_list[2]) == 3 and msg_str[-1] == "*":
        return 3

    # sender = CC, receiver = soldier
    elif int(msg_list[0]) == 2 and int(msg_list[2]) == 1:
        return 4

    else:
        return 0


# Split Message
def split_message(msg_str):
    msg_list = msg_str.split(".")
    return msg_list


# isOpen
def is_open(IP, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((IP, port))
        result = True
    except:
        result = False
    sock.close()
    return result

