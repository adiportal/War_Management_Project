import logging
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


# Exit
# def exit(sock, serverAddress):
#     sendMessage('-1', sock, serverAddress)
#     print("\nGood Bye :)")
#     logging.debug("Closing Soldier...")
#     quit()


# sendMassage
def handleMessage(sendMsg, sock, CCAddress):

    recMsg = ''
    try:
        sock.sendto(sendMsg.encode(), CCAddress)

        logging.debug("Message has been sent to CC {} : {}".format(CCAddress, sendMsg))

        recMsg, CCAddress = sock.recvfrom(65527)
        recMsg = recMsg.decode('utf-8')

        case = Utility.switchCase(recMsg)

        if case == 1:
            # print receive message
            print("The message '{}' reached to Company Commander".format(recMsg))
            logging.debug("The message '{}' reached to CC {}".format(recMsg, CCAddress))

        elif case == 2:
            print("The message '{}' reached to Battalion Commander".format(recMsg))
            logging.debug("The message '{}' reached to BC {}".format(recMsg, Utility.getBCAddress()))

        else:
            logging.ERROR("An invalid message has reached: \'{}\'".format(recMsg))

    except:
        logging.error("The message '{}' did'nt reached to CC {}".format(recMsg, CCAddress))
        print("The message '{}' did'nt reached to the Company Commander!!".format(recMsg))

# **Main**
sock = Utility.getSock()
sock.settimeout(5)
sock.bind(Utility.getSoldierAddress())

CCAddress = Utility.getCCAddress()

msg_str = ""

while msg_str == "":
    print("Write Your Message:")
    msg_str = input()
    handleMessage(msg_str, sock, CCAddress)
    msg_str = ""




