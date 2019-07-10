import socket
import logging


# Initialize the Logger
logging.basicConfig(filename = 'Log.log', level = logging.DEBUG, format = '%(asctime)s : %(levelname)s : App1 : %(message)s')

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

def getApp1Address():
    IP = '127.0.0.1'
    port = 5001
    return (IP, port)

# getServerAddress
def getApp2Address():
    IP = '127.0.0.1'
    port = 5002
    return (IP, port)


# Exit
def exit(sock, serverAddress):
    sendMessage('-1', sock, serverAddress)
    print("\nGood Bye :)")
    logging.debug("Closing App1...")
    quit()

# sendMassage
def sendMessage(sendMsg, sock, app2Address):

    try:
        sock.sendto(sendMsg.encode(), app2Address)

        logging.debug("Message has been sent to App2 {} : {}".format(app2Address, sendMsg))

        recMsg, app2Address = sock.recvfrom(1024)
        recMsg = recMsg.decode('utf-8')

        if recMsg != '-1':
            # print receive message
            print("The message '{}' reached to the App2".format(recMsg))
        logging.debug("The message '{}' reached to {}".format(recMsg, app2Address))

    except:
        logging.error("The message '{}' did'nt reached to {}".format(recMsg, app2Address))
        if sendMsg != '-1':
            print("The message '{}' did'nt reached to the App2!!".format(recMsg))
        else:
            print("App2 is still working!!")
        logging.critical("App2 is still working!!")
