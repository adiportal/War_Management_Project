import threading

import Utility


def listen():
    print('Listening...\n')

    while True:
        # set max size of message
        rec_msg, rec_address = sock.recvfrom(65527)

        # decoding the message to String
        rec_msg = rec_msg.decode('utf-8')

        print(str(rec_address) + "  >>  " + rec_msg)
        rec_msg = "*" + rec_msg
        sock.sendto(rec_msg.encode(), rec_address)


sock = Utility.get_sock()
sock.bind(('127.0.0.1', 5002))

listen_thread = threading.Thread(target=listen)
listen_thread.start()

msg_str = ""

while msg_str == "":
    print("Write Your Message:")
    msg_str = input()

    sock.sendto(msg_str.encode(), ('127.0.0.1', 5001))

    msg_str = ""
