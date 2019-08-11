import socket
import logging

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : BC : %(message)s')

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

# Check Message
def checkMSG(msg_str):

#    if msg_str[:2] == 'CC':
#        return 'CC'

    if msg_str[:2] == 'BC':
        return 'BC'

    else:
        return 'null'


# **Main**
# Initialize Server Address
BCAddress = getBCAddress()

# Initialize Socket
sock = getSock()

# Bind the socket with the address
sock.bind(BCAddress)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    recMsg, CCAddress = sock.recvfrom(1024)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    check = checkMSG(recMsg)

    if check != 'BC':
        logging.ERROR("an invalid message has reached: \'{}\'".format(recMsg))

    else:
        # printing the message and the Sender Address
        print('Received message from Soldier {} : {}'.format(CCAddress, recMsg))
        logging.debug("Received message from Soldier {} : {}".format(CCAddress, recMsg))

        sock.sendto(recMsg.encode(), CCAddress)



