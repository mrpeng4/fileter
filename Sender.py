import socket
import time
import os

PORT = 5001
BUFFER_SIZE = 1024
user_showed_up = True

def path_input():
    user_filepath = input("Please provide the path of the file: ")

    file_path = user_filepath
    file_size_bytes = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    return file_name, file_size_bytes, user_filepath

def sender_side():
    global user_showed_up

    file_name, file_size, user_filepath = path_input()
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sender.bind(("0.0.0.0", 5002))
    print("waiting for a receiver...")
    sender.settimeout(2)

    offer = f"OFFER|{file_name}|{file_size//1000000}mb".encode()
    deadline = time.time() + 300

    while time.time() < deadline:
        sender.sendto(offer, ("255.255.255.255", 5000))
        try:
            data, addr = sender.recvfrom(BUFFER_SIZE)
            user_showed_up = True
        except socket.timeout:
            user_showed_up = False
            continue

        if data == b"READY":
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
            break

sender_side()

if user_showed_up == False:
    print("No receiver showed up. File not sent.")
else:
    print("Success!")