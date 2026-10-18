import socket
import time
import os
import tqdm

BROADCAST_PORT = 5000
TCP_PORT = 5003
CHUNK_SIZE = 65536

def path_input():
    user_filepath = input("Please provide the path of the file: ")

    file_size_bytes = os.path.getsize(user_filepath)
    file_name = os.path.basename(user_filepath)

    return file_name, file_size_bytes, user_filepath

def sender_side():
    file_name, file_size, user_filepath = path_input()

    # UDP socket: used to shout "I have a file"
    shouter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    shouter.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # TCP socket: the begger/receiver connects here to get the chonky file
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen(1)
    server.settimeout(2)

    offer = "OFFER|" + file_name + "|" + str(file_size)
    offer = offer.encode()

    print("Waiting for a receiver...")
    end_time = time.time() + 300
    receiver_found = False

    while time.time() < end_time:
        shouter.sendto(offer, ("255.255.255.255", BROADCAST_PORT))
        try:
            connection, addr = server.accept()
            receiver_found = True
            break
        except socket.timeout:
            pass

    if receiver_found == False:
        print("No receiver showed up. File not sent.")
        shouter.close()
        server.close()
        return

    print(f"Receiver connected {addr[0]}, sending...")

    # just a progress bar idk why can't change the text color
    # it only lets me change the bar color :(
    progress_bar = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=file_size)

    file = open(user_filepath, "rb")
    while True:
        chunk = file.read(CHUNK_SIZE)
        if chunk == b"":
            break
        connection.sendall(chunk)
        progress_bar.update(len(chunk))

    file.close()

    connection.close()
    shouter.close()
    server.close()
    print("Success!")
    print("Come back later ;)")