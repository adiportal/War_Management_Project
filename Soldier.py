import socket
import logging
import datetime
import Utility

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Soldier : %(message)s')

class Soldier():

    # Attributes
    ID = 1
    companyNumber = 0
    x = 0
    y = 0
    ammo = 0
    HP = 0

    def __init__(self, companyNumber, location, ammo):
        self.ID = Soldier.ID
        Soldier.ID += 1
        self.companyNumber = companyNumber
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100



# get Soldier Address
def getSoldierAddress():
    IP = '127.0.0.1'
    port = 5001
    return (IP, port)

# get Company Commander Address
def getCCAddress():
    IP = '127.0.0.1'
    port = 5002
    return (IP, port)

# get Battalion Commander Address
def getBCAddress():
    IP = '127.0.0.1'
    port = 5003
    return (IP, port)

# Exit
def exit(sock, serverAddress):
    sendMessage('-1', sock, serverAddress)
    print("\nGood Bye :)")
    logging.debug("Closing Soldier...")
    quit()

# Check Message
def checkMSG(msg_str):

    if msg_str[:2] == 'CC':
        return 'CC'

    elif msg_str[:2] == 'BC':
        return 'BC'

    else:
        return 'null'


# sendMassage
def sendMessage(sendMsg, sock, CCAddress):

    recMsg = ''
    try:
        sock.sendto(sendMsg.encode(), CCAddress)

        logging.debug("Message has been sent to CC {} : {}".format(CCAddress, sendMsg))

        recMsg, CCAddress = sock.recvfrom(1024)
        recMsg = recMsg.decode('utf-8')

        if checkMSG(recMsg) == 'CC':
            # print receive message
            print("The message '{}' reached to Company Commander".format(recMsg))
            logging.debug("The message '{}' reached to CC {}".format(recMsg, CCAddress))

        elif checkMSG(recMsg) == 'BC':
            print("The message '{}' reached to Battalion Commander".format(recMsg))
            logging.debug("The message '{}' reached to BC {}".format(recMsg, getBCAddress()))

        else:
            logging.ERROR("An invalid message has reached: \'{}\'".format(recMsg))

    except:
        logging.error("The message '{}' did'nt reached to CC {}".format(recMsg, CCAddress))
        print("The message '{}' did'nt reached to the Company Commander!!".format(recMsg))

# **Main**
sock = Utility.getSock()
sock.settimeout(5)
sock.bind(getSoldierAddress())

CCAddress = getCCAddress()

msg_str = ""

while msg_str == "":
    msg_str = input()
    check = checkMSG(msg_str)

    if (check == "CC" or check == "BC"):
        sendMessage(msg_str, sock, CCAddress)
        msg_str = ""

    else:
        print("The Message you Entered is not correct")
        msg_str = ""
        continue
