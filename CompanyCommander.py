import socket
import logging
import Utility

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : CC : %(message)s')

class CompanyCommander():

    # Attributes
    ID = 1
    companyNumber = 0
    x = 0
    y = 0
    ammo = 0
    HP = 0

    def _init_(self, companyNumber, location, ammo):
        self.ID = CompanyCommander.ID
        CompanyCommander.ID += 1
        self.companyNumber = companyNumber
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100


def handleMessage(recMsg, recAddress):
    case = Utility.switchCase(recMsg)

    if case == 1:

        # printing the message and the client Address
        print('Received message from Soldier {} : {}'.format(recAddress, recMsg))
        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))

        sock.sendto(recMsg.encode(), Utility.getSoldierAddress())

    elif case == 2:

        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))
        sock.sendto(recMsg.encode(), Utility.getBCAddress())

    elif case == 3:

        recMsg = recMsg[:-1]

        logging.debug("Received message from BC {} : {}".format(recAddress, recMsg))
        sock.sendto(recMsg.encode(), Utility.getSoldierAddress())

    else:           # case = 0
        logging.ERROR("An invalid message has reached: \'{}\'".format(recMsg))

# *Main*
# Initialize Server Address
CCAddress = Utility.initCCAddress()

sock = Utility.getSock()

if sock == 0:   # 3 CompanyCommanders is open
    quit()

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