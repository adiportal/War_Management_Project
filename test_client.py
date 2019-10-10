# import threading
#
# import Utility
#
#
# def listen():
#     print('Listening...\n')
#
#     while True:
#         # set max size of message
#         rec_msg, rec_address = sock.recvfrom(65527)
#
#         # decoding the message to String
#         rec_msg = rec_msg.decode('utf-8')
#
#         print(rec_msg)
#
#
# sock = Utility.get_sock()
# sock.bind(('127.0.0.1', 5001))
#
# listen_thread = threading.Thread(target=listen)
# listen_thread.start()
#
# msg_str = ""
#
# while msg_str == "":
#     print("Write Your Message:")
#     msg_str = input()
#
#     sock.sendto(msg_str.encode(), ('127.0.0.1', 5002))
#
#     msg_str = ""
import pickle
import socket
import Entities
from Entities import Packet
from Entities import InitMessage
from Entities import UpdateFieldObjectMessage
from Entities import MoveOrderMessage

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 5001))
s1 = Entities.Soldier(1, (2, 3.4), 25)

# Init FieldObject Message
packet = Packet(1, 1, 2, 4, InitMessage(s1))
byte_packet = pickle.dumps(packet)

print(pickle.loads(byte_packet))

sock.sendto(byte_packet, ("127.0.0.1", 5002))

# Update FieldObject Message
packet = Packet(1, 1, 2, 1, UpdateFieldObjectMessage(s1))
byte_packet = pickle.dumps(packet)

sock.sendto(byte_packet, ("127.0.0.1", 5002))

print(pickle.loads(byte_packet))

# Move Order Message
packet = Packet(2, 1, 1, 2, MoveOrderMessage(1, 1, (2, 3)))
byte_packet = pickle.dumps(packet)

sock.sendto(byte_packet, ("127.0.0.1", 5002))

print(pickle.loads(byte_packet))