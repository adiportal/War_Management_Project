import socket
import logging

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

# **Main**
# Initialize Server Address
CCAddress = getCCAddress()

sock = getSock()

# Bind the socket with the address
sock.bind(CCAddress)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    recMsg, recAddress = sock.recvfrom(1024)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    if (recMsg[:2] == "CC" and recAddress == getSoldierAddress()):

        # printing the message and the client Address
        print('Received message from Soldier {} : {}'.format(recAddress, recMsg[4:]))
        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))

        sock.sendto(recMsg.encode(), recAddress)

    elif (recMsg[:2] == "BC" and recAddress == getSoldierAddress()):

        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))
        sock.sendto(recMsg.encode(), getBCAddress())

    elif (recMsg[:2] == "BC" and recAddress == getBCAddress()):

        logging.debug("Received message from BC {} : {}".format(recAddress, recMsg))
        sock.sendto(recMsg.encode(), getSoldierAddress())
    else:
        continue


