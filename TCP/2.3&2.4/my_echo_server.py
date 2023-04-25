from socket import socket, AF_INET, SOCK_STREAM

def server():
    with socket(AF_INET, SOCK_STREAM) as server:
        try:
            server.bind(('0.0.0.0', 8820))
        except OSError:
            print("Try again layer")
            return
        print("Echo Server is running")
        server.listen()
        client, client_address = server.accept()
        print("Client is connected")
        data = client.recv(1024)
        print(f"Client sent: {data.decode()}")
        client.send(data)
        client.close()

server()