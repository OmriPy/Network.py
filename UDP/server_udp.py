from socket import socket, AF_INET, SOCK_DGRAM

SERVER_IP = '127.0.0.1'
PORT = 8821
MAX_DATA_SIZE = 1024

def server():
    with socket(AF_INET, SOCK_DGRAM) as server:
        try:
            server.bind((SERVER_IP, PORT))
        except OSError:
            print("Try again later")
            return
        print("Server is running\n")
        while True:
            data, client_address = server.recvfrom(MAX_DATA_SIZE)
            data = data.decode()
            print(data)
            if data.upper() == "EXIT":
                return


server()
