import socket
import logging

logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Middle : %(message)s')



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

    IP = '127.0.0.1'
    port = 5005

    clientAddress = (IP, port)
    sockClient.bind(clientAddress)


server()
msg_str = "NONE"
client()
