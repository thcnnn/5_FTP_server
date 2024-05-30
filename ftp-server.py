import socket
import threading
import os
import logging
import hashlib
import json
from commands import process_request
# Configuration
PORT = 9090
SERVER_DIRECTORY = 'server_directory'
USER_FILE = 'users.json'
ADMIN_USER = 'admin'
ADMIN_PASSWORD = hashlib.sha256('adminpass'.encode()).hexdigest()

# Ensure server directory exists
if not os.path.exists(SERVER_DIRECTORY):
    os.makedirs(SERVER_DIRECTORY)

# Setup logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    authenticated = False
    while not authenticated:
        conn.send('Register or Login (r/l): '.encode())
        choice = conn.recv(1024).decode().strip()

        if choice == 'r':
            conn.send('New Username: '.encode())
            username = conn.recv(1024).decode().strip()
            conn.send('New Password: '.encode())
            password = conn.recv(1024).decode().strip()
            response = register_user(username, password)
            conn.send((response + '\n').encode())
            if 'successfully' in response:
                authenticated = True
        elif choice == 'l':
            conn.send('Username: '.encode())
            username = conn.recv(1024).decode().strip()
            conn.send('Password: '.encode())
            password = conn.recv(1024).decode().strip()

            if (username == ADMIN_USER and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD) or (
                    username in users and hashlib.sha256(password.encode()).hexdigest() == users[username]):
                authenticated = True
                conn.send('Authentication successful\n'.encode())
            else:
                conn.send('Authentication failed\n'.encode())

    if authenticated:
        conn.send("Available commands:\n"
                  "pwd - Print working directory\n"
                  "ls - List directory contents\n"
                  "mkdir <directory> - Create directory\n"
                  "rmdir <directory> - Remove directory\n"
                  "rm <file> - Remove file\n"
                  "rename <old_name> <new_name> - Rename file or directory\n"
                  "upload <filename> <content> - Upload file\n"
                  "download <filename> - Download file\n"
                  "exit - Exit\n".encode())

    while authenticated:
        try:
            request = conn.recv(1024).decode()
            if not request:
                break
            print(f"[REQUEST] {addr}: {request}")
            user_directory = os.path.join(SERVER_DIRECTORY, username)
            response = process_request(request, user_directory)
            conn.send((response + '\n').encode())
        except ConnectionResetError:
            break

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")


def register_user(username, password):
    if username in users:
        return 'Username already exists'
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[username] = hashed_password
    save_users(users)
    user_directory = os.path.join(SERVER_DIRECTORY, username)
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)
    return 'User registered successfully'


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on port {PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    users = load_users()
    start_server()
