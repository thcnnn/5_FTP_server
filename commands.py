import os
import shutil
import logging

SERVER_DIRECTORY = 'server_directory'


def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def process_request(request, user_directory, user_quota=1024 * 1024 * 100):
    try:
        command, *args = request.strip().split()
        response = 'Invalid command '

        if command == 'pwd':
            response = os.getcwd()
        elif command == 'ls':
            response = '; '.join(os.listdir(user_directory))
        elif command == 'mkdir':
            if len(args) != 1:
                response = 'Usage: mkdir <directory>'
            else:
                os.makedirs(os.path.join(user_directory, args[0]), exist_ok=True)
                response = f"Directory {args[0]} created"
        elif command == 'rmdir':
            if len(args) != 1:
                response = 'Usage: rmdir <directory>'
            else:
                shutil.rmtree(os.path.join(user_directory, args[0]))
                response = f"Directory {args[0]} deleted"
        elif command == 'rm':
            if len(args) != 1:
                response = 'Usage: rm <file>'
            else:
                os.remove(os.path.join(user_directory, args[0]))
                response = f"File {args[0]} deleted"
        elif command == 'rename':
            if len(args) != 2:
                response = 'Usage: rename <old_name> <new_name>'
            else:
                os.rename(os.path.join(user_directory, args[0]), os.path.join(user_directory, args[1]))
                response = f"Renamed {args[0]} to {args[1]}"
        elif command == 'upload':
            if len(args) != 2:
                response = 'Usage: upload <filename> <content>'
            else:
                file_size = len(args[1])
                if get_directory_size(user_directory) + file_size > user_quota:
                    response = 'Quota exceeded'
                else:
                    with open(os.path.join(user_directory, args[0]), 'w') as f:
                        f.write(args[1])
                    response = f"File {args[0]} uploaded"
        elif command == 'download':
            if len(args) != 1:
                response = 'Usage: download <filename>'
            else:
                with open(os.path.join(user_directory, args[0]), 'r') as f:
                    response = f.read()
        elif command == 'exit':
            response = 'exit'

        logging.info(f"Command: {request} Response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error processing command: {request} Error: {e}")
        return str(e)
