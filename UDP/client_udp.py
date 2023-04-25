from socket import socket, AF_INET, SOCK_DGRAM

SERVER_IP = '127.0.0.1'
PORT = 8821
MAX_DATA_SIZE = 1024

def client():
    with socket(AF_INET, SOCK_DGRAM) as client:
        msg = ""
        while msg.upper() != "EXIT":
            msg = input("Enter message:\t")
            client.sendto(msg.encode(), (SERVER_IP, PORT))


client()