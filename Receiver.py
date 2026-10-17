import socket
import tqdm

PORT = 5000
TCP_PORT = 5003
BUFFER_SIZE = 1024
CHUNK_SIZE = 65536

def receiver_side():
    #wait for the shout of the broadcast not someone screaming
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind(("0.0.0.0", PORT))
    print("Waiting for a broadcast...")
    data, addr = receiver.recvfrom(BUFFER_SIZE)
    receiver.close()

    # the message looks like: OFFER|photo.jpg|2000 This is not a sale offer
    parts = data.decode().split("|")
    file_name = parts[1]
    file_size = int(parts[2])
    sender_ip = addr[0]

    print(f"{sender_ip} | {file_name} | {file_size/1000000:.2f}MB")
    user_answer = input("Do you want to receive this file (enter y/n): ").lower().strip()

    if user_answer != "y":
        print("No selected file not saved")
        return

    #connect to the sender and get the chonky file
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((sender_ip, TCP_PORT))
    print("Receiving file...")

    progress_bar = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=file_size)

    received = 0
    f = open("received_" + file_name, "wb")

    while received < file_size:
        bytes_left = file_size - received
        if bytes_left < CHUNK_SIZE:
            amount = bytes_left
        else:
            amount = CHUNK_SIZE

        chunk = tcp.recv(amount)
        if chunk == b"":
            break

        f.write(chunk)
        received = received + len(chunk)
        progress_bar.update(len(chunk))

    f.close()
    progress_bar.close()
    tcp.close()

    print(f"Saved as received_{file_name} | {received/1000000:.2f}MB )")

receiver_side()