import socket
import tqdm

PORT = 5000
BUFFER_SIZE = 1024

def receiver_side():
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind(("0.0.0.0", PORT))
    print("Waiting for a broad cast")
    data, addr = receiver.recvfrom(BUFFER_SIZE)
    print(data.decode())
    user_answer = input("Do you want to receive this file (enter y/n): ").lower().strip()
    if user_answer == "y":
        receiver.sendto(b"READY", addr)
        print("Waiting for file...")

        while True:
            file_name, _ = receiver.recvfrom(BUFFER_SIZE)
            if not file_name.startswith(b"OFFER|"):
                break
        file_size, _ = receiver.recvfrom(BUFFER_SIZE)
        file_name = file_name.decode()
        print(file_name)
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
        print(f"Saved as received_{file_name} ({received//1000000} megabytes)")
    else:
        print("No selected file not saved")

receiver_side()