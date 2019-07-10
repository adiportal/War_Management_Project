import socket
import logging

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : App2 : %(message)s')

# Initialize Socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.debug("Socket Successfully Created!")
except socket.error as err:
    logging.error("Socket creation failed with error {}".format(err))


def getApp1Address():
    IP = '127.0.0.1'
    port = 5001
    return (IP, port)

# getServerAddress
def getApp2Address():
    IP = '127.0.0.1'
    port = 5002
    return (IP, port)

def getApp3Address():
    IP = '127.0.0.1'
    port = 5003
    return (IP, port)

# Initialize Server Address
app2Address = getApp2Address()

# Bind the socket with the address
sock.bind(app2Address)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    recMsg, recAddress = sock.recvfrom(1024)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    if (recMsg[:4] == "App2" and recAddress == getApp1Address()):

        # printing the message and the client Address
        print('Received message from App1 {} : {}'.format(recAddress, recMsg[4:]))
        logging.debug("Received message from App1 {} : {}".format(recAddress, recMsg))

        sock.sendto(recMsg.encode(), recAddress)

    if recMsg == '-1':
        print("Closing App3...")
        logging.debug('Closing App3...')
        quit()

