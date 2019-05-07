import socket
import logging

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Server : %(message)s')

# Initialize Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
IP = '127.0.0.1'
port = 5002

# Initialize Client Address
clientAddress = (IP, port)

# Bind the socket with the address
sock.bind(clientAddress)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    msg_bytes, clientAddress = sock.recvfrom(1024)

    # decoding the message to String
    msg_str = msg_bytes.decode('utf-8')

    # printing the message and the client Address
    print('Received message from client {} : {}'.format(clientAddress, msg_str))
    logging.debug("Received message from Client {} : {}".format(clientAddress, msg_str))

    sock.sendto(msg_str.encode(), clientAddress)

    if msg_str == '-1':
        print("Closing Server...")
        logging.debug('Closing Server...')
        quit()
