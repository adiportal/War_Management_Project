import socket
import logging
import Utility

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : BC : %(message)s')



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
BCAddress = Utility.getBCAddress()

# Initialize Socket
sock = Utility.getSock()

# Bind the socket with the address
sock.bind(BCAddress)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    recMsg, CCAddress = sock.recvfrom(65527)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    check = checkMSG(recMsg)

    if check != 'BC':
        logging.ERROR("an invalid message has reached: \'{}\'".format(recMsg))

    else:
        # printing the message and the Sender Address
        print('Received message from Soldier {} : {}'.format(CCAddress, recMsg[2:]))
        logging.debug("Received message from Soldier {} : {}".format(CCAddress, recMsg))

        recMsg = "3.1." + recMsg[4:]
        sock.sendto(recMsg.encode(), CCAddress)



