import socket
import logging

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : App3 : %(message)s')

# Initialize Socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.debug("Socket Successfully Created!")
except socket.error as err:
    logging.error("Socket creation failed with error {}".format(err))

IP = '127.0.0.1'
port = 5003

# Initialize Server Address
app3Address = (IP, port)

# Bind the socket with the address
sock.bind(app3Address)


print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    recMsg, app2Address = sock.recvfrom(1024)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    # printing the message and the client Address
    print('Received message from App2 {} : {}'.format(app2Address, recMsg))
    logging.debug("Received message from App2 {} : {}".format(app2Address, recMsg))

    sock.sendto(recMsg.encode(), app2Address)

    if recMsg == '-1':
        print("Closing App3...")
        logging.debug('Closing App3...')
        quit()

