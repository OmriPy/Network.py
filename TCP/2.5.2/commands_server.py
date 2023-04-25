from socket import socket, AF_INET, SOCK_STREAM
from typing import Callable
from utils import *

COMMANDS: Dict[str, Callable] = {
    NAME: name,
    TIME: time,
    RAND: rand,
    QUIT: quit
}

def server():
    with socket(AF_INET, SOCK_STREAM) as server:
        try:
            server.bind(('0.0.0.0', PORT))
        except OSError:
            print('Try again later')
            return
        print('Commands Server is running')
        server.listen()
        client, client_address = server.accept()
        print('Client is connected\n')
        while True:
            data = client.recv(DEFAULT_DATA_SIZE).decode()
            print(data)
            if data in COMMANDS.keys():
                client.send(COMMANDS.get(data)().encode())
            else:
                client.send('Command not found'.encode())
            if data == QUIT:
                client.close()
                return


server()
