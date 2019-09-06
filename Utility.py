import logging
import socket

logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Utility : %(message)s')


# getSock
def getSock():
    # Initialize socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    return sock


# get Soldier Address
def getSoldierAddress():
    IP = '127.0.0.1'
    port = 5001
    return (IP, port)


# get Company Commander Address
def getCCAddress():
    IP = '127.0.0.1'
    port = 5004
    count = 0

    while (isOpen(IP, port)) == False and count == 3:
        port += 1
        count += 1

    if count == 3:
        return 0

    return (IP, port)



# get Battalion Commander Address
def getBCAddress():
    IP = '127.0.0.1'
    port = 5003
    return (IP, port)


# Check Message                     MSG ICD: Sender.Receiver.MSG (str)
def switchCase(msg_str):

    msg_list = splitMessage(msg_str)

    # sender = Soldier, receiver = CC
    if int(msg_list[0]) == 1 and int(msg_list[1]) == 2:
        return 1

    # sender = Soldier, receiver = BC
    elif int(msg_list[0]) == 1 and int(msg_list[1]) == 3 and msg_str[-1] != "*":
        return 2

    # sender = BC, receiver = CC -> Soldier
    elif int(msg_list[0]) == 1 and int(msg_list[1]) == 3 and msg_str[-1] == "*":
        return 3

    else:
        return 0


# Split Message
def splitMessage(msg_str):
    msg_list = msg_str.split(".")
    return msg_list


# isOpen
def isOpen(IP, port):
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   try:
      sock.connect((IP, int(port)))
      sock.shutdown(2)
      return True
   except:
      return False