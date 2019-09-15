import logging
import Utility

# Initialize the Logger
logging.basicConfig(filename='CompanyCommander.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : CC : %(message)s')


def handle_message(rec_msg, rec_address):
    case = Utility.switch_case(rec_msg)

    if case == 1:

        # printing the message and the client Address
        print('Received message from Soldier {} : {}'.format(rec_address, rec_msg))
        logging.debug("Received message from Soldier {} : {}".format(rec_address, rec_msg))

        sock.sendto(rec_msg.encode(), Utility.get_soldier_address())

    elif case == 2:

        logging.debug("Received message from Soldier {} : {}".format(rec_address, rec_msg))
        sock.sendto(rec_msg.encode(), Utility.get_bc_address())

    elif case == 3:

        rec_msg = rec_msg[:-1]

        logging.debug("Received message from BC {} : {}".format(rec_address, rec_msg))
        sock.sendto(rec_msg.encode(), Utility.get_soldier_address())

    else:           # case = 0
        logging.ERROR("An invalid message has reached: \'{}\'".format(rec_msg))


# *Main*
# Initialize Server Address
cc_address = Utility.init_cc_address()

if cc_address == 0:   # 3 CompanyCommanders is open
    print("There are 3 Company Commanders already open in the system")
    quit()

sock = Utility.get_sock()


# Bind the socket with the address
sock.bind(cc_address)
logging.info(sock)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    rec_msg, rec_address = sock.recvfrom(65527)

    # decoding the message to String
    rec_msg = rec_msg.decode('utf-8')

    handle_message(rec_msg, rec_address)


