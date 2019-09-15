import logging
import Utility
import Entities

# Initialize the Logger
logging.basicConfig(filename = 'SoldierLog.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Soldier : %(message)s')

class UDP():
    # sendMassage
    def handle_message(send_msg, sock, cc_address):

        rec_msg = ''
        try:
            sock.sendto(send_msg.encode(), cc_address)

            logging.debug("Message has been sent to CC {} : {}".format(cc_address, send_msg))

            rec_msg, cc_address = sock.recvfrom(65527)
            rec_msg = rec_msg.decode('utf-8')

            case = Utility.switch_case(rec_msg)

            if case == 1:
                # print receive message
                print("The message '{}' reached to Company Commander".format(rec_msg))
                logging.debug("The message '{}' reached to CC {}".format(rec_msg, cc_address))

            elif case == 2:
                print("The message '{}' reached to Battalion Commander".format(rec_msg))
                logging.debug("The message '{}' reached to BC {}".format(rec_msg, Utility.get_bc_address()))

            else:
                logging.ERROR("An invalid message has reached: \'{}\'".format(rec_msg))

        except:
            logging.error("The message '{}' did'nt reached to CC {}".format(rec_msg, cc_address))
            print("The message '{}' did'nt reached to the Company Commander!!".format(rec_msg))

    # **Main**
    soldier_address = Utility.init_soldier_address()

    if soldier_address == 0:  # there is open Soldier
        print("There is open Soldier")
        quit()

    sock = Utility.get_sock()
    sock.settimeout(5)
    sock.bind(Utility.get_soldier_address())

    msg_str = ""

    while msg_str == "":
        #print("Write Your Message:")
        #msg_str = input()

        cc_address = Utility.get_cc_address(msg_str[0])

        if cc_address == 0:
            print("ERROR: INVALID Company Number")
            msg_str = ""
            continue

        msg_str = "1." + msg_str
        handle_message(msg_str, sock, cc_address)
        msg_str = ""

