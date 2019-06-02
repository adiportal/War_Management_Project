import socket
import logging

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Server : %(message)s')

# Initialize Socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.debug("Socket Successfully Created!")
except socket.error as err:
    logging.error("Socket creation failed with error {}".format(err))

IP = '127.0.0.1'
port = 5002

# Initialize Server Address
serverAddress = (IP, port)

# Bind the socket with the address
sock.bind(serverAddress)


print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    msg_bytes, middleAddress = sock.recvfrom(1024)

    # decoding the message to String
    msg_str = msg_bytes.decode('utf-8')

    # printing the message and the client Address
    print('Received message from client {} : {}'.format(middleAddress, msg_str))
    logging.debug("Received message from Client {} : {}".format(middleAddress, msg_str))

    sock.sendto(msg_str.encode(), middleAddress)

    if msg_str == '-1':
        print("Closing Server...")
        logging.debug('Closing Server...')
        quit()

