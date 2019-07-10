import socket
import logging
import random
import time
from pynput import keyboard

program_running = True

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Client : %(message)s')


# sendMassage
def sendMessage(msg_str, sock, serverAddress):

    try:
        sock.sendto(msg_str.encode(), serverAddress)

        logging.debug("Message has been sent to Server {} : {}".format(serverAddress, msg_str))

        msg_str, serverAddress = sock.recvfrom(1024)
        msg_str = msg_str.decode('utf-8')

        if msg_str != '-1':
            # print receive message
            print("The message '{}' reached to the server".format(msg_str))
        logging.debug("The message '{}' reached to {}".format(msg_str, serverAddress))

    except:
        logging.error("The message '{}' did'nt reached to {}".format(msg_str, serverAddress))
        if msg_str != '-1':
            print("The message '{}' did'nt reached to the server!!".format(msg_str))
        else:
            print("The server is still working!!")
        logging.critical("The server is still working!!")


# randomNum
def randomNum():
    return str(random.randint(0, 1000000))


# getSock
def getSock():
    # Initialize socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Socket Successfully Created!")
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))
    sock.settimeout(5)

    return sock


# getServerAddress
def getServerAddress():
    IP = '127.0.0.1'
    port = 5002
    return (IP, port)


def getClientAddress():
    IP = '127.0.0.1'
    port = 5003
    return (IP, port)

def getMiddle_SAddress():
    IP = '192.168.1.1'
    port = 5004
    return (IP, port)


# Exit
def exit(sock, serverAddress):
    sendMessage('-1', sock, serverAddress)
    print("\nGood Bye :)")
    logging.debug("Closing Client...")
    quit()


# On Press
def on_press(key):
    global program_running
    logging.debug("User Pressed '{}'".format(key))
    if key == keyboard.Key.esc or key == keyboard.Key.space:
        program_running = False
        return False


# Main

sock = getSock()
sock.bind(getClientAddress())

middleAddress = getMiddle_SAddress()

# print("Welcome to UDP Client/Server App\nPress [Esc] / [Space] for Exit")
# time.sleep(2)

strr = input()
msg_str = "Sconnect"
sendMessage(msg_str, sock, middleAddress)





# with keyboard.Listener(on_press=on_press) as listener:
#     while program_running == True:
#         msg_str = randomNum()
#         sendMessage(msg_str, sock, serverAddress)
#         time.sleep(2)
#     listener.join()
#
#     exit(sock, serverAddress)





