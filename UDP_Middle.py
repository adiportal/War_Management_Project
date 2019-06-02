import socket
import logging

logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Middle : %(message)s')

# sendMassage
def sendMessage(msg_str, sock, senderAddress, senderName, receiverAddress, receiverName):

    try:
        sock.sendto(msg_str.encode(), receiverAddress)

        logging.debug("Message has been sent to {} {} : {}".format(receiverName, receiverAddress, msg_str))

        msg_str, receiverAddress = sock.recvfrom(1024)
        msg_str = msg_str.decode('utf-8')

        if msg_str != '-1':
            # print receive message
            print("The message '{}' reached to the {}".format(receiverName, msg_str))
            logging.debug("The message '{}' reached to {}".format(msg_str, receiverAddress))

        elif msg_str == '-1'& senderName == "Server":
            sock.sendto(msg_str.encode(), getClientAddress())

            logging.debug("Message has been sent to {} {} : {}".format(receiverName, receiverAddress, msg_str))

    except:
        logging.error("The message '{}' did'nt reached to {}".format(msg_str, receiverAddress))
        if msg_str != '-1':
            print("The message '{}' did'nt reached to the {}!!".format(msg_str, receiverName))
        else:
            print("The server is still working!!")
        logging.critical("The server is still working!!")

def server():
    try:
        sockServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    IP = '127.0.0.1'
    port = 5004
    serverAddress = (IP, port)

    sockServer.bind(serverAddress)

    while True:

        # set max size of message
        msg_bytes, clientAddress = sockServer.recvfrom(1024)

        global msg_str
        # decoding the message to String
        msg_str = msg_bytes.decode('utf-8')

        # printing the message and the client Address
        print('Received message from client {} : {}'.format(clientAddress, msg_str))
        logging.debug("Received message from Client {} : {}".format(clientAddress, msg_str))

        sockServer.sendto(msg_str.encode(), clientAddress)

        if msg_str == '-1':
            print("Closing Server...")
            logging.debug('Closing Server...')
            quit()



def client():
    try:
        sockClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    sockClient.settimeout(5)

    clientAddress = getClientAddress()
    sockClient.bind(clientAddress)

# getClientAddress
def getClientAddress():
    return ('127.0.0.1', 5005)



