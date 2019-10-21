import logging
import Utility

# Initialize the Logger
logging.basicConfig(filename='BattalionCommanderLog.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : '
                                                                                      'BC : %(message)s')


def handle_message(rec_msg):
    rec_msg_list = rec_msg.split(".")

    if Utility.switch_case(rec_msg) == 0:
        logging.ERROR("an invalid message has reached: \'{}\'".format(rec_msg))
    else:
        rec_address = Utility.get_cc_address(rec_msg_list[1])
        # printing the message and the Sender Address
        print('Received message from Soldier {} : {}'.format(rec_address, rec_msg))
        logging.debug("Received message from Soldier {} : {}".format(rec_address, rec_msg))

        rec_msg = rec_msg + "*"
        sock.sendto(rec_msg.encode(), rec_address)


# *Main*
# Initialize Server Address
bc_address = Utility.init_bc_address()

if bc_address == 0:   # there is open BattalionCommanders
    print("There is open Battalion Commanders")
    quit()

# Initialize Socket
sock = Utility.get_sock()

# Bind the socket with the address
sock.bind(bc_address)

logging.info(sock)

print('Listening')
logging.debug('Listening')

while True:

    # set max size of message
    rec_msg, rec_address = sock.recvfrom(65527)

    # decoding the message to String
    rec_msg = rec_msg.decode('utf-8')

    handle_message(rec_msg)