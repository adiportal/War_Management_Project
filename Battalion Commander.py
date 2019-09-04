import logging
import Utility

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : BC : %(message)s')

def handleMessage(recMsg, recAddress):
    if Utility.switchCase(recMsg) == 0:
        logging.ERROR("an invalid message has reached: \'{}\'".format(recMsg))

    else:
        # printing the message and the Sender Address
        print('Received message from Soldier {} : {}'.format(recAddress, recMsg))
        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))

        recMsg = recMsg + "*"
        sock.sendto(recMsg.encode(), Utility.getCCAddress())

# *Main*
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
    recMsg, recAddress = sock.recvfrom(65527)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    handleMessage(recMsg, recAddress)