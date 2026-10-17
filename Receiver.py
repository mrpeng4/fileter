import socket
import tqdm

PORT = 5001
BUFFER_SIZE = 4136

def receiver_side():
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind(("0.0.0.0", PORT))
    receiver.sendto(b"READY", ("127.0.0.1", 5002))
    print("Waiting for file...")

    file_name, _ = receiver.recvfrom(BUFFER_SIZE)
    file_size, _ = receiver.recvfrom(BUFFER_SIZE)
    file_name = file_name.decode()
    file_size = int(file_size.decode())

    progress_bar = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))

    received = 0
    with open("received_" + file_name, "wb") as f:
        while received < file_size:
            chunk, _ = receiver.recvfrom(BUFFER_SIZE)
            f.write(chunk)
            received += len(chunk)
            progress_bar.update(len(chunk))

    receiver.close()
    print(f"Saved as received_{file_name} ({received} bytes)")

receiver_side()