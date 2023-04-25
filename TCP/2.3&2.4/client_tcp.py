from socket import socket, AF_INET, SOCK_STREAM

def client():
    with socket(AF_INET, SOCK_STREAM) as client:
        client.connect(('127.0.0.1', 8820))
        print("Client is connected")
        client.send("hello there".encode())
        data = client.recv(1024)
        print(f"Server sent: {data.decode()}")

client()
