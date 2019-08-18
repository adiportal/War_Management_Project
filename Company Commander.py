import socket
import logging
from concurrent.futures import ThreadPoolExecutor

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : CC : %(message)s')


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
    port = 5002
    return (IP, port)

# get Battalion Commander Address
def getBCAddress():
    IP = '127.0.0.1'
    port = 5003
    return (IP, port)

# Check Message
def checkMSG(msg_str):

    if msg_str[:2] == 'CC':
        return 'CC'

    elif msg_str[:2] == 'BC':
        return 'BC'

    else:
        return 'null'

# receiveMsg
def receiveMsg(sock):
    # set max size of message
    recMsg, recAddress = sock.recvfrom(1024)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    check = checkMSG(recMsg)

    if (check == "CC" and recAddress == getSoldierAddress()):

        # printing the message and the client Address
        print('Received message from Soldier {} : {}'.format(recAddress, recMsg[2:]))
        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))

        pool.submit(sendMsg, recMsg, recAddress)

    elif (check == "BC" and recAddress == getSoldierAddress()):

        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))
        pool.submit(sendMsg, recMsg, getBCAddress())

    elif (check == "BC" and recAddress == getBCAddress()):

        logging.debug("Received message from BC {} : {}".format(recAddress, recMsg))
        pool.submit(sendMsg, recMsg, getSoldierAddress())
    else:
        return


# sendMsg
def sendMsg(msg, address):
    print("started")
    sock.sendto(msg, address)

# **Main**
# Initialize Server Address
CCAddress = getCCAddress()

sock = getSock()

# Bind the socket with the address
sock.bind(CCAddress)

print('Listening')
logging.debug('Listening')

while True:
    with ThreadPoolExecutor(max_workers=2) as pool:
        pool.submit(receiveMsg, sock)
