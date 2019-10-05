import logging
import Utility
import threading

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Soldier : %(message)s')

company1 = []
company2 = []
company3 = []


def listen():
    print('Listening...\n')

    while True:
        # set max size of message
        rec_msg, rec_address = sock.recvfrom(65527)

        # decoding the message to String
        rec_msg = rec_msg.decode('utf-8')
        if rec_msg:
            receive_handler(rec_msg, rec_address)


def main_menu():
    ans = ""
    while ans == "":
        ans = input(Utility.main_menu())
        if not (1 <= int(ans) <= 2):
            print("You should Enter a number (1-2)")
            ans = ""

    if int(ans) == Utility.MenuOptions.new_field_object.value:
        list_and_msg = Utility.new_field_object_opt()
        object_list = list_and_msg[Utility.ListAndMsg.list.value]
        object_str = list_and_msg[Utility.ListAndMsg.msg.value]

        new_object_field = Utility.create_object_field(object_str)
        company_num = new_object_field.get_company_num()

        if company_num == Utility.Company.company1.value:
            company1.append(new_object_field)

        elif company_num == Utility.Company.company2.value:
            company2.append(new_object_field)

        else:
            company3.append(new_object_field)

        return str(Utility.Sender.soldier.value) + \
               " :: " + \
               object_list[Utility.ObjectListIndex.company_num.value] + \
               " :: " + \
               str(Utility.Receiver.company_commander.value) + \
               " :: " + \
               str(Utility.MessageType.new_field_object.value) + \
               " :: " + \
               list_and_msg[Utility.ListAndMsg.msg.value]
    else:
        report_location()


def report_location():
    for field_object in company1:
        msg = str(Utility.Sender.soldier.value) + \
              " :: " + \
              str(field_object.get_company_num()) + \
              " :: " + \
              str(Utility.Receiver.company_commander.value) + \
              " :: " + \
              str(Utility.MessageType.report_location.value) + \
              " :: " + \
              str(field_object.get_company_num()) + \
              " ; " + \
              str(field_object.get_id()) + \
              " ; " + \
              field_object.get_str_location()

        send_handler(msg)


def receive_handler(msg, address):
    case = Utility.sender_receiver_switch_case(msg)

    if case == Utility.Case.approval.value:
        print("The Message '{}' Approved".format(msg[1:]))
        return
    else:
        print(str(address) + " >> " + msg)


# sendMassage
def send_handler(msg):

    rec_msg = ''
    try:
        sock.sendto(msg.encode(), cc_address)

    #     logging.debug("Message has been sent to CC {} : {}".format(cc_address, msg))
    #
    #     # rec_msg, cc_address = sock.recvfrom(65527)
    #     # rec_msg = rec_msg.decode('utf-8')
    #
    #     if case == Utility.Case.soldier_to_cc.value:
    #         # print receive message
    #         print("The message '{}' reached to Company Commander".format(rec_msg))
    #         logging.debug("The message '{}' reached to CC {}".format(rec_msg, cc_address))
    #
    #     elif case == Utility.Case.soldier_to_bc.value:
    #         print("The message '{}' reached to Battalion Commander".format(rec_msg))
    #         logging.debug("The message '{}' reached to BC {}".format(rec_msg, Utility.get_bc_address()))
    #
    #     else:
    #         logging.ERROR("An invalid message has reached: \'{}\'".format(rec_msg))
    #
    except:
        logging.error("The message '{}' didn't reached to CC {}".format(rec_msg, cc_address))
        print("The message '{}' did'nt reached to the Company Commander!!".format(rec_msg))


# **Main**
sock = Utility.get_sock()
sock.bind(Utility.get_soldier_address())

listen_thread = threading.Thread(target=listen)
listen_thread.start()

msg_str = ""

while msg_str == "":
    msg_str = main_menu()

    cc_address = Utility.get_cc_address(1)

    if cc_address == 0:
        print("ERROR: INVALID Company Number")
        msg_str = ""
        continue

    if msg_str != "":
        send_handler(msg_str)
    msg_str = ""


