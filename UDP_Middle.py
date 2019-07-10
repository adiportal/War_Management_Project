import socket
import logging

logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Middle : %(message)s')

clients = []

# sendMassage
def sendMessage(msg_str, senderAddress, senderName, receiverAddress, receiverName):

    # serverClosed = False # Changing to True if Server app is closed
    # clientClosed = False # Changing to True if Client app is closed

    try:
        if msg_str != '-1' & receiverName == "Server":          # Client -> Middle -> Server
            print("blabla")
            # Middle -> Server
            sockClient.sendto(msg_str.encode(), receiverAddress)

            logging.debug("Message has been sent to {} {} : {}".format(receiverName, receiverAddress, msg_str))

            msg_str, receiverAddress = sockClient.recvfrom(1024)
            msg_str = msg_str.decode('utf-8')

            # print receive message
            print("The message '{}' from {} reached to the {}".format(msg_str, senderName, receiverName))
            logging.debug("The message '{}' from {} reached to {}".format(msg_str, senderAddress, receiverAddress))

            # Middle -> Client
            sockClient.sendto(msg_str.encode(), senderAddress)

            logging.debug("Approval message has been sent to {} {} : {}".format(receiverName, receiverAddress, msg_str))

            msg_str, senderAddress = sockClient.recvfrom(1024)
            msg_str = msg_str.decode('utf-8')

            logging.debug("The approval message '{}' reached to {}".format(msg_str, senderAddress))

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

    middle_SAddress = getMiddle_SAddress()

    sockServer.bind(middle_SAddress)

    while True:

        # set max size of message
        msg_bytes, senderAddress = sockServer.recvfrom(1024)

        # decoding the message to String
        msg_str = msg_bytes.decode('utf-8')

        # printing the message and the client Address
        print('Received message from Client {} : {}'.format(senderAddress, msg_str[1:]))
        logging.debug("Received message from Client {} : {}".format(senderAddress, msg_str[1:]))

        if msg_str[1:] == "connect":
            if not clients:
                clients.append(senderAddress)
                sockServer.sendto(senderAddress + "Connected", senderAddress)
            else:
                clients.append(senderAddress)
                for client in clients:
                    sockServer.sendto(client + "Connected", senderAddress)

        if msg_str[0] == "S":

            sendMessage(msg_str[1:], getMiddle_SAddress(), "Middle_S", getMiddle_CAddress(), "Middle_C")
            print("ports")


        elif msg_str[0] == "M":
            sockServer.sendto(msg_str.encode(), senderAddress)

        if msg_str == '-1':
            print("Closing Server...")
            logging.debug('Closing Server...')
            quit()



def client():
    try:
        global sockClient
        sockClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    sockClient.settimeout(5)

    middle_CAddress = getMiddle_CAddress()
    sockClient.bind(middle_CAddress)

    while True:

        # set max size of message
        msg_bytes, receiverAddress = sockClient.recvfrom(1024)

        # decoding the message to String
        msg_str = msg_bytes.decode('utf-8')
        print("port done")
        sendMessage(msg_str[1:], getMiddle_CAddress(), "Middle_C", getServerAddress(), "Server")
        print("message to server")

# getClientAddress
def getClientAddress():
    return ('127.0.0.1', 5003)

# getServerAddress
def getServerAddress():
    return ('127.0.0.1', 5002)

# getMiddle_CAddress
def getMiddle_CAddress():
    return ('127.0.0.1', 5005)

# getMiddle_SAddress
def getMiddle_SAddress():
    return ('127.0.0.1', 5004)

# Main
server()
client()





