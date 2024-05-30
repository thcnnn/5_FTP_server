import socket

HOST = 'localhost'
PORT = 9090

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        response = sock.recv(1024).decode()
        print(response, end='')

        while True:
            request = input()
            sock.send(request.encode())
            if request.strip().lower() == 'exit':
                break
            response = sock.recv(1024).decode()
            print(response, end='')

if __name__ == "__main__":
    start_client()
