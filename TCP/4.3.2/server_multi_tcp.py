from socket import socket, AF_INET, SOCK_STREAM
import select
from typing import List

SERVER_IP = '0.0.0.0'
PORT = 5555
MAX_DATA_LENGTH = 1024

def print_clients(clients: List[socket]):
    for sock in clients:
        print(f'\t{sock.getpeername()}')

def server():
    with socket(AF_INET, SOCK_STREAM) as server:
        print("Setting up server...")
        try:
            server.bind((SERVER_IP, PORT))
        except OSError:
            print("Try again later")
            return
        print("Server is up and running")
        print("Listening for clients...")
        server.listen()
        clients = []
        while True:
            ready_to_read, ready_to_write, in_error = select.select([server] + clients, [], [])
            for current_socket in ready_to_read:
                if current_socket is server:
                    client, client_address = current_socket.accept()
                    clients.append(client)
                    print(f"New client has joined!\t{client_address}")
                    print_clients(clients)
                else:
                    print("New data from client!")
                    data = current_socket.recv(MAX_DATA_LENGTH)
                    if data.decode() == ' ':
                        print('Connection closed')
                        clients.remove(current_socket)
                        current_socket.close()
                        print_clients(clients)
                    else:
                        print(data.decode())
                        current_socket.send(data)



server()