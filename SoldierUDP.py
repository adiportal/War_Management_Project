import logging
import Utility

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Soldier : %(message)s')


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
sock = Utility.get_sock()
sock.settimeout(5)
sock.bind(Utility.get_soldier_address())

msg_str = ""

while msg_str == "":
    print("Write Your Message:")
    msg_str = input()

    cc_address = Utility.get_cc_address(msg_str[0])

    if cc_address == 0:
        print("ERROR: INVALID Company Number")
        msg_str = ""
        continue

    msg_str = "1." + msg_str
    handle_message(msg_str, sock, cc_address)
    msg_str = ""



# import threading
# import logging
# import time
#
# import Utility
# from concurrent.futures import ThreadPoolExecutor
#
#
# def background_listener():
#
#     sock = Utility.get_sock()
#     sock.bind(Utility.get_listen_soldier_address())
#
#     while True:
#         # set max size of message
#         rec_msg, rec_address = listen_sock.recvfrom(65527)
#
#         # decoding the message to String
#         rec_msg = rec_msg.decode('utf-8')
#         print(rec_msg)
#
#         sock.close()
#         sock = Utility.get_sock()
#         time.sleep(.1)
#
#
# def try_func():
#
#     while True:
#         print(Utility.main_menu())
#         msg_list = Utility.new_field_object_opt()
#         msg_str = Utility.create_init_message(msg_list)
#         sock = Utility.get_sock()
#         sock.sendto(send_msg.encode(), Utility.get_cc_address())
#
#         # set max size of message
#         rec_msg, rec_address = listen_sock.recvfrom(65527)
#
#         # decoding the message to String
#         rec_msg = rec_msg.decode('utf-8')
#         print(rec_msg)
#
#         sock.close()
#         sock = Utility.get_sock()
#         time.sleep(.1)
#
#
# def send_msg():
#     sock = Utility.get_sock()
#
#     print(Utility.main_menu())
#     msg_list = Utility.new_field_object_opt()
#     msg_str = Utility.create_init_message(msg_list)
#
#     while msg_str == "":
#         msg_str = input("Write Your Message:")
#         msg_str = "1." + msg_str
#         msg_list = msg_str.split(".")
#
#         cc_address = Utility.get_cc_address(msg_list[Utility.MessageIndexes.company_num.value])
#
#         if cc_address == Utility.Case.error.value:
#             print("ERROR: INVALID Company Number")
#             msg_str = ""
#             continue
#
#         handle_message(msg_str, sender_sock, cc_address)
#         msg_str = ""
#
#
# def handle_message(send_msg, sock, cc_address):
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
#         if case == Utility.Case.soldier_to_cc.value:
#             # print receive message
#             print("The message '{}' reached to Company Commander".format(rec_msg))
#             logging.debug("The message '{}' reached to CC {}".format(rec_msg, cc_address))
#
#         elif case == Utility.Case.soldier_to_bc.value:
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
# listen_sock = Utility.get_sock()
# # sender_sock = Utility.get_sock()
# # sock.settimeout(5)
#
# listen_sock.bind(Utility.get_listen_soldier_address())
# # listen_sock.bind(Utility.get_sender_soldier_address())
#
# # now threading1 runs regardless of user input
# # threading1 = threading.Thread(target=background)
# # threading1.daemon = True
# # threading1.start()
#
# max_workers = 2
# with ThreadPoolExecutor[max_workers] as executor:
#     task1 = executor.submit(background_listener)
#     task2 = executor.submit(send_msg())

