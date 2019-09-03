import socket
import logging
import datetime
import Utility


# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Soldier : %(message)s')

# getSock
def getSock():
    # Initialize socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))
    sock.settimeout(5)

    return sock

# get Soldier Address
def getSoldierAddress():
    IP = '127.0.0.1'
    port = 5001
    return (IP, port)

# get Company Commander Address
def getCCAddress():
    IP = '127.0.0.1'
    port = 5002
    return (IP, port)

# get Battalion Commander Address
def getBCAddress():
    IP = '127.0.0.1'
    port = 5003
    return (IP, port)

# Exit
def exit(sock, serverAddress):
    sendMessage('-1', sock, serverAddress)
    print("\nGood Bye :)")
    logging.debug("Closing Soldier...")
    quit()

# Check Message
def checkMSG(msg_str):

    if msg_str[:2] == 'CC':
        return 'CC'

    elif msg_str[:2] == 'BC':
        return 'BC'

    else:
        return 'null'


# sendMassage
def sendMessage(sendMsg, sock, CCAddress):

    recMsg = ''
    try:
        sock.sendto(sendMsg.encode(), CCAddress)

        logging.debug("Message has been sent to CC {} : {}".format(CCAddress, sendMsg))

        recMsg, CCAddress = sock.recvfrom(1024)
        recMsg = recMsg.decode('utf-8')

        if checkMSG(recMsg) == 'CC':
            # print receive message
            print("The message '{}' reached to Company Commander".format(recMsg))
            logging.debug("The message '{}' reached to CC {}".format(recMsg, CCAddress))

        elif checkMSG(recMsg) == 'BC':
            print("The message '{}' reached to Battalion Commander".format(recMsg))
            logging.debug("The message '{}' reached to BC {}".format(recMsg, getBCAddress()))

        else:
            logging.ERROR("An invalid message has reached: \'{}\'".format(recMsg))

    except:
        logging.error("The message '{}' did'nt reached to CC {}".format(recMsg, CCAddress))
        print("The message '{}' did'nt reached to the Company Commander!!".format(recMsg))

# **Main**

sock = getSock()
sock.bind(getSoldierAddress())

CCAddress = getCCAddress()

msg_str = ""

while msg_str == "":
    msg_str = (1, datetime.datetime.now(), 2, num, 1, (soldierNum, location))
    check = checkMSG(msg_str)

    if (check == "CC" or check == "BC"):
        sendMessage(msg_str, sock, CCAddress)
        msg_str = ""

    else:
        print("The Message you Entered is not correct")
        msg_str = ""
        continue

