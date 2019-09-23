# import logging
# import Utility
#
# # Initialize the Logger
# logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Soldier : %(message)s')
#
#
# # sendMassage
# def handle_message(send_msg, sock, cc_address):
#
#     rec_msg = ''
#     try:
#         sock.sendto(send_msg.encode(), cc_address)
#
#         logging.debug("Message has been sent to CC {} : {}".format(cc_address, send_msg))
#
#         rec_msg, cc_address = sock.recvfrom(65527)
#         rec_msg = rec_msg.decode('utf-8')
#
#         case = Utility.switch_case(rec_msg)
#
#         if case == 1:
#             # print receive message
#             print("The message '{}' reached to Company Commander".format(rec_msg))
#             logging.debug("The message '{}' reached to CC {}".format(rec_msg, cc_address))
#
#         elif case == 2:
#             print("The message '{}' reached to Battalion Commander".format(rec_msg))
#             logging.debug("The message '{}' reached to BC {}".format(rec_msg, Utility.get_bc_address()))
#
#         else:
#             logging.ERROR("An invalid message has reached: \'{}\'".format(rec_msg))
#
#     except:
#         logging.error("The message '{}' did'nt reached to CC {}".format(rec_msg, cc_address))
#         print("The message '{}' did'nt reached to the Company Commander!!".format(rec_msg))
#
#
# # **Main**
# sock = Utility.get_sock()
# sock.settimeout(5)
# sock.bind(Utility.get_soldier_address())
#
# msg_str = ""
#
# while msg_str == "":
#     print("Write Your Message:")
#     msg_str = input()
#
#     cc_address = Utility.get_cc_address(msg_str[0])
#
#     if cc_address == 0:
#         print("ERROR: INVALID Company Number")
#         msg_str = ""
#         continue
#
#     msg_str = "1." + msg_str
#     handle_message(msg_str, sock, cc_address)
#     msg_str = ""
#


import threading
import logging
import Utility


def background():
    while True:
        # set max size of message
        rec_msg, rec_address = sock.recvfrom(65527)

        # decoding the message to String
        rec_msg = rec_msg.decode('utf-8')
        print(rec_msg)


def handle_message(send_msg, sock, cc_address):
    rec_msg = ''
    try:
        sock.sendto(send_msg.encode(), cc_address)

        logging.debug("Message has been sent to CC {} : {}".format(cc_address, send_msg))

        rec_msg, cc_address = sock.recvfrom(65527)
        rec_msg = rec_msg.decode('utf-8')

        case = Utility.switch_case(rec_msg)

        if case == Utility.Case.soldier_to_cc.value:
            # print receive message
            print("The message '{}' reached to Company Commander".format(rec_msg))
            logging.debug("The message '{}' reached to CC {}".format(rec_msg, cc_address))

        elif case == Utility.Case.soldier_to_bc.value:
            print("The message '{}' reached to Battalion Commander".format(rec_msg))
            logging.debug("The message '{}' reached to BC {}".format(rec_msg, Utility.get_bc_address()))

        else:
            logging.ERROR("An invalid message has reached: \'{}\'".format(rec_msg))

    except:
        logging.error("The message '{}' did'nt reached to CC {}".format(rec_msg, cc_address))
        print("The message '{}' did'nt reached to the Company Commander!!".format(rec_msg))


sock = Utility.get_sock()
# sock.settimeout(5)
sock.bind(Utility.get_soldier_address())

# now threading1 runs regardless of user input
threading1 = threading.Thread(target=background)
threading1.daemon = True
threading1.start()


msg_str = ""

while msg_str == "":
    msg_str = input("Write Your Message:")
    msg_str = "1." + msg_str
    msg_list = msg_str.split(".")

    cc_address = Utility.get_cc_address(msg_list[Utility.MessageIndexes.company_num.value])

    if cc_address == Utility.Case.error.value:
        print("ERROR: INVALID Company Number")
        msg_str = ""
        continue

    handle_message(msg_str, sock, cc_address)
    msg_str = ""
