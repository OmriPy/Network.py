from socket import socket, AF_INET, SOCK_STREAM
from utils import *

def client():
    with socket(AF_INET, SOCK_STREAM) as client:
        client.connect(('127.0.0.1', PORT))
        print("Client is connected")
        cmd = ""
        while cmd != QUIT:
            cmd = input("Enter command:\t").upper()
            client.send(cmd.encode())
            data = client.recv(DEFAULT_DATA_SIZE).decode()
            print(f'{data}\n')


client()