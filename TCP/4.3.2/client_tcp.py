from socket import socket, AF_INET, SOCK_STREAM

SERVER_IP = '127.0.0.1'
PORT = 5555
MAX_DATA_LENGTH = 1024

def client():
    with socket(AF_INET, SOCK_STREAM) as client:
        client.connect((SERVER_IP, PORT))
        msg = 'hi'
        while msg != '':
            msg = input("Enter message:\t")
            if msg == '':
                client.send(' '.encode())
                break
            client.send(msg.encode())


client()
