import socket
import logging
import Utility

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : CC : %(message)s')


def handleMessage(rec_msg, rec_address):
    case = Utility.switchCase(rec_msg)

    if case == 1:

        # printing the message and the client Address
        print('Received message from Soldier {} : {}'.format(rec_address, rec_msg))
        logging.debug("Received message from Soldier {} : {}".format(rec_address, rec_msg))

        sock.sendto(rec_msg.encode(), Utility.getSoldierAddress())

    elif case == 2:

        logging.debug("Received message from Soldier {} : {}".format(rec_address, rec_msg))
        sock.sendto(rec_msg.encode(), Utility.get_bc_address())

    elif case == 3:

        rec_msg = rec_msg[:-1]

        logging.debug("Received message from BC {} : {}".format(rec_address, rec_msg))
        sock.sendto(rec_msg.encode(), Utility.getSoldierAddress())

    else:           # case = 0
        logging.ERROR("An invalid message has reached: \'{}\'".format(rec_msg))

# *Main*
# Initialize Server Address
CCAddress = Utility.initCCAddress()

if CCAddress == 0:   # 3 CompanyCommanders is open
    print("There are 3 Company Commanders already open in the system")
    quit()

sock = Utility.getSock()


# Bind the socket with the address
sock.bind(CCAddress)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    recMsg, recAddress = sock.recvfrom(65527)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    handleMessage(recMsg, recAddress)


