import logging
import Utility
import threading

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Soldier : %(message)s')


def listen():
    print('Listening...\n')

    while True:
        # set max size of message
        rec_msg, rec_address = sock.recvfrom(65527)

        # decoding the message to String
        rec_msg = rec_msg.decode('utf-8')
        if rec_msg:
            handle_message(rec_msg, sock, rec_address)


# sendMassage
def handle_message(msg, sock, cc_address):

    case = Utility.switch_case(msg)

    if case == Utility.Case.approval.value:
        print("The Message '{}' Approved".format(msg[1:]))

    else:
        rec_msg = ''
        try:
            sock.sendto(msg.encode(), cc_address)

            logging.debug("Message has been sent to CC {} : {}".format(cc_address, msg))

            rec_msg, cc_address = sock.recvfrom(65527)
            rec_msg = rec_msg.decode('utf-8')


            if case == Utility.Case.soldier_to_cc.value:
                # print receive message
                print("The message '{}' reached to Company Commander".format(rec_msg))
                logging.debug("The message '{}' reached to CC {}".format(rec_msg, cc_address))

            elif case == Utility.Case.soldier_to_bc:
                print("The message '{}' reached to Battalion Commander".format(rec_msg))
                logging.debug("The message '{}' reached to BC {}".format(rec_msg, Utility.get_bc_address()))

            else:
                logging.ERROR("An invalid message has reached: \'{}\'".format(rec_msg))

        except:
            logging.error("The message '{}' didn't reached to CC {}".format(rec_msg, cc_address))
            print("The message '{}' did'nt reached to the Company Commander!!".format(rec_msg))


# **Main**
sock = Utility.get_sock()
old_timeout = sock.gettimeout()  # Save
# print(old_timeout)
sock.settimeout(old_timeout)
sock.bind(Utility.get_soldier_address())

listen_thread = threading.Thread(target=listen)
listen_thread.start()

msg_str = ""

while msg_str == "":
    print("Write Your Message:")
    msg_str = input()

    cc_address = ("127.0.0.1", 5002)

    # if cc_address == 0:
    #     print("ERROR: INVALID Company Number")
    #     msg_str = ""
    #     continue

    msg_str = "1." + msg_str
    handle_message(msg_str, sock, cc_address)
    msg_str = ""


