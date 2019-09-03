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


# Check Message
def checkMSG(msg_str):

    if msg_str[:2] == 'CC':
        return 'CC'

    elif msg_str[:2] == 'BC':
        return 'BC'

    else:
        return 'null'

def sendMessage(recMsg, recAddress):
    check = checkMSG(recMsg)

    if (check == "CC" and recAddress == Utility.getSoldierAddress()):

        # printing the message and the client Address
        print('Received message from Soldier {} : {}'.format(recAddress, recMsg[2:]))
        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))

        sock.sendto(recMsg.encode(), recAddress)

    elif (check == "BC" and recAddress == Utility.getSoldierAddress()):

        logging.debug("Received message from Soldier {} : {}".format(recAddress, recMsg))
        sock.sendto(recMsg.encode(), Utility.getBCAddress())

    elif (check == "BC" and recAddress == Utility.getBCAddress()):

        logging.debug("Received message from BC {} : {}".format(recAddress, recMsg))
        sock.sendto(recMsg.encode(), Utility.getSoldierAddress())
    else:
        logging.ERROR("An invalid message has reached: \'{}\'".format(recMsg))

# *Main*
# Initialize Server Address
CCAddress = Utility.getCCAddress()

sock = Utility.getSock()

# Bind the socket with the address
sock.bind(CCAddress)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    recMsg, recAddress = sock.recvfrom(1024)

    # decoding the message to String
    recMsg = recMsg.decode('utf-8')

    sendMessage(recMsg, recAddress)