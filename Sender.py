import socket
import time
import os

PORT = 5001
BUFFER_SIZE = 4136

def path_input():
    user_filepath = input("Please provide the path of the folder: ")

    file_path = user_filepath
    file_size_bytes = os.path.getsize(file_path)
    splitted_file_path = file_path.split("/")
    file_name = splitted_file_path[-1]

    return file_name, file_size_bytes, user_filepath

def sender_side():
    file_name, file_size, user_filepath = path_input()

    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.bind(("0.0.0.0", 5002))
    sender.settimeout(300)

    print("Waiting up to 5 minutes for a receiver...")
    try:
        _, addr = sender.recvfrom(BUFFER_SIZE)
    except socket.timeout:
        print("No receiver showed up. File not sent.")
        sender.close()
        return

    sender.sendto(file_name.encode(), addr)
    sender.sendto(str(file_size).encode(), addr)

    with open(user_filepath, "rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sender.sendto(chunk, addr)
            time.sleep(0.0008)

    sender.close()

sender_side()