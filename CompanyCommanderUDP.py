import logging
import threading

import Utility

# Initialize the Logger
logging.basicConfig(filename='CompanyCommander.log', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : CC : %(message)s')

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
        ans = input(Utility.cc_main_menu())
        if int(ans) != 1:
            print("You can chose only 1 option for now")
            ans = ""

    company_num = ""
    while company_num == "":
        company_num = input("Enter company num: \n")
        while not (1 <= int(company_num) <= 3):
            company_num = input("You should Enter a number between 1-3: \n")

    field_object_id = ""
    contain = False
    while field_object_id == "":
        field_object_id = input("Enter FieldObject ID: \n")
        for field_object in company1:
            if field_object.get_id() == int(field_object_id):
                contain = True
                break
        if not contain:
            print("Company 1 does not contain an FieldObject #" + field_object_id)
            field_object_id = ""

    new_x = ""
    while new_x == "":
        new_x = input("Enter new X: \n")

    new_y = ""
    while new_y == "":
        new_y = input("Enter new Y: \n")

    new_location = new_x + "," + new_y

    return Utility.create_move_to_message(company_num, field_object_id, new_location)


def receive_handler(msg, address):
    sender_receiver_case = Utility.sender_receiver_switch_case(msg)
    opt_case = Utility.options_switch_case(msg)
    full_msg_list = msg.split(" :: ")
    msg_str = full_msg_list[Utility.FullMessageIndexes.message.value]
    msg_list = msg_str.split(" ; ")

    if sender_receiver_case == Utility.Case.soldier_to_cc.value:

        # printing the message and the client Address
        print('Received message from Soldier {} >> {}'.format(address, msg))
        logging.debug("Received message from Soldier {} >> {}".format(address, msg))
        if opt_case == Utility.MessageType.new_field_object.value:
            new_object_field = Utility.create_object_field(msg_str)
            print(new_object_field)

            company_num = new_object_field.get_company_num()

            if company_num == Utility.Company.company1.value:
                company1.append(new_object_field)

            elif company_num == Utility.Company.company2.value:
                company2.append(new_object_field)

            else:
                company3.append(new_object_field)

        if opt_case == Utility.MessageType.report_location.value:
            location = msg_list[Utility.ReportMessageIndexes.location.value].split(",")

            if int(msg_list[Utility.ReportMessageIndexes.company_num.value]) == Utility.Company.company1.value:
                updated = False
                for object_field in company1:
                    if object_field.get_id() == int(msg_list[Utility.ReportMessageIndexes.id.value]):
                        object_field.update_location(float(location[Utility.Location.X.value]), float(location[Utility.Location.Y.value]))
                        print("#" + str(object_field.get_id()) + " location was updated to: " + object_field.get_str_location())
                        updated = True
                        break

                if not updated:
                    print("Company 1 doe's not contain #" + msg_list[Utility.ReportMessageIndexes.id.value])

            elif int(msg_list[Utility.ReportMessageIndexes.company_num.value]) == Utility.Company.company2.value:
                updated = False
                for object_field in company2:
                    if object_field.get_id() == int(msg_list[Utility.ReportMessageIndexes.id.value]):
                        object_field.update_location(float(location[Utility.Location.X.value]),
                                                     float(location[Utility.Location.Y.value]))
                        print("#" + str(object_field.get_id()) + " location was updated to: " + object_field.get_str_location())
                        updated = True
                        break

                if not updated:
                    print("Company 2 doe's not contain #" + msg_list[Utility.ReportMessageIndexes.id.value])

            else:
                updated = False
                for object_field in company3:
                    if object_field.get_id() == int(msg_list[Utility.ReportMessageIndexes.id.value]):
                        object_field.update_location(float(location[Utility.Location.X.value]),
                                                     float(location[Utility.Location.Y.value]))
                        print("#" + str(object_field.get_id()) + " location was updated to: " + object_field.get_str_location())
                        updated = True
                        break

                if not updated:
                    print("Company 3 doe's not contain #" + msg_list[Utility.ReportMessageIndexes.id.value])

        msg = "*" + msg
        sock.sendto(msg.encode(), Utility.get_soldier_address())

    # elif sender_receiver_case == 2:
    #
    #     logging.debug("Received message from Soldier {} : {}".format(address, msg))
    #     sock.sendto(msg.encode(), Utility.get_bc_address())
    #
    # elif sender_receiver_case == 3:
    #
    #     msg = msg[:-1]
    #
    #     logging.debug("Received message from BC {} : {}".format(address, msg))
    #     sock.sendto(msg.encode(), Utility.get_soldier_address())

    else:           # sender_receiver_case = 0
        logging.ERROR("An invalid message has reached: \'{}\'".format(msg))


def send_handler(msg):

    rec_msg = ''
    try:
        sock.sendto(msg.encode(), soldier_address)

    except:
        logging.error("The message '{}' didn't reached to CC {}".format(rec_msg, cc_address))
        print("The message '{}' did'nt reached to the Company Commander!!".format(rec_msg))


# Main
# Initialize Server Address
cc_address = Utility.init_cc_address()

if cc_address == 0:   # 3 CompanyCommanders is open
    print("There are 3 Company Commanders already open in the system")
    quit()

sock = Utility.get_sock()


# Bind the socket with the address
sock.bind(cc_address)
logging.info(sock)

listen_thread = threading.Thread(target=listen)
listen_thread.start()

msg_str = ""

while msg_str == "":
    msg_str = main_menu()

    soldier_address = ("127.0.0.1", 5001)

    # if cc_address == 0:
    #     print("ERROR: INVALID Company Number")
    #     msg_str = ""
    #     continue

    if msg_str != "":
        send_handler(msg_str)
    msg_str = ""
