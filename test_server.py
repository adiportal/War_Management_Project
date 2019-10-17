import pickle
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 5002))

print('Listening')

while True:
    # set max size of message
    rec_msg, rec_address = sock.recvfrom(65527)

    # decoding the message to String
    rec_msg = pickle.loads(rec_msg)

    print(rec_msg)