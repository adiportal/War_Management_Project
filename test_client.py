import pickle
import socket

from Entities import Packet

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 5001))


packet = Packet(1, 1, 2, 1, "hello")
byte_packet = pickle.dumps(packet)

sock.sendto(byte_packet, ("127.0.0.1", 5002))

print(byte_packet)

print(pickle.loads(byte_packet))