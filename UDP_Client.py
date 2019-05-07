import socket
import logging
import random
import time
from pynput import keyboard

program_running = True

# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : Client : %(message)s')

# sendMassage
def sendMessage(data, sock, serverAddress):

    try:
        sock.sendto(data.encode('utf-8'), serverAddress)

        logging.debug("Message has been sent to Server {} : {}".format(serverAddress, data))

        data, serverAddress = sock.recvfrom(1024)
        text = data.decode('utf-8')

        if text != '-1':
            # print receive message
            print("The message '{}' reached to the server".format(text))
        logging.debug("The message '{}' reached to {}".format(text, serverAddress))

    except:
        logging.error("The message '{}' did'nt reached to {}".format(data, serverAddress))
        if data != '-1':
            print("The message '{}' did'nt reached to the server!!".format(data))
        else:
            print("The server is still working!!")
        logging.critical("The server is still working!!")
# randomNum
def randomNum():
    return str(random.randint(0,1000000))

    # getSock
def getSock():
    # Initialize socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    return sock

# getAddress
def getAddress():
    IP = '127.0.0.1'
    port = 5002

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
serverAddress = getAddress()

print("Welcome to UDP Client/Server App\nPress [Esc] / [Space] for Exit")
time.sleep(2)

with keyboard.Listener(on_press=on_press) as listener:
    while program_running == True:
        data = randomNum()
        sendMessage(data, sock, serverAddress)
        time.sleep(2)
    listener.join()

    exit(sock, serverAddress)





