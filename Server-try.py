# Multi-peer echo server
import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("127.0.0.1", 5000))

# create a set to keep track of the connected clients
clients = set()

while True:
    data, address = udp_socket.recvfrom(512)
    print("Received %s from %s:%d" %(data, address[0], address[1]))
    text = data.decode("UTF-8")

    if text == "add_me":
        clients.add(address)
        udp_socket.sendto(b"You have been added to the client list", address)
        print("There are now %d clients connected" %len(clients))

    elif address in clients:
        for client in clients:
            udp_socket.sendto(data, client)
    else:
        udp_socket.sendto(b"Sorry you don't appear to be in the client list.", address)