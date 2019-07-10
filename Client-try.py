import socket

# Set up our sending socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("127.0.0.1", 5001))

# Send greeting to the receiver
data = b"add_me"
udp_socket.sendto(data,("127.0.0.1", 5000))

data, address = udp_socket.recvfrom(512)
print("Received %s from %s:%d" %(data, address[0], address[1]))

strr = input()

data = b"hello from client 1"
udp_socket.sendto(data,("127.0.0.1", 5000))

data, address = udp_socket.recvfrom(512)
print("Received %s from %s:%d" %(data, address[0], address[1]))
