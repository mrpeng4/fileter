import socket
import tqdm
import SaverUI
from plyer import notification

BROADCAST_PORT = 5000
TCP_PORT = 6000
BUFFER_SIZE = 1024
CHUNK_SIZE = 65536

def receiver_side():
    # wait for the shout of the broadcast not someone screaming
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.settimeout(300)

    try:
        receiver.bind(("0.0.0.0", BROADCAST_PORT))
    except OSError:
        print("The port seems to be occupied. Please try again in a few minutes.\nThis happens because someone else is currently waiting to receive a file.\nMulti-user support is coming later, just wait for now :)")
        return
    else:
        print("Waiting for a broadcast...")
        try:
            data, addr = receiver.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("Timed out waiting for a sender.\nNo one broadcasted a file in 5 minutes.\nTry again when someone wants to send.")
            receiver.close()
            return
        receiver.close()

        # the message looks like: OFFER|photo.jpg|2000 This is not a sale offer
        try:
            parts = data.decode().split("|")
            file_name = parts[1]
            file_size = int(parts[2])
            sender_ip = addr[0]
        except UnicodeDecodeError:
            print("Received a garbled message from the sender.\nTheir broadcast was corrupted. Ask them to restart and try again.")
            return
        except (IndexError, ValueError):
            print("Received an incomplete message from the sender.\nThe broadcast data was malformed. Ask them to restart and try again.")
            return

        print(f"File name: {file_name}")
        print(f"File size: {file_size / 1000000:.2f}MB")
        print(f"File From: {sender_ip}\n")

        print("+-----------------------------------+")
        print("| [1] Yes                           |")
        print("| [2] No                            |")
        print("+-----------------------------------+")

        try:
            user_answer = input("Do you want to receive this file: ").lower().strip()
        except (KeyboardInterrupt, EOFError):
            print("\nYou exited the prompt.\nNo file received. Run the receiver again when ready.")
            return
        print("\n")

        if user_answer != "1":
            print("No selected file not saved")
            return

        # connect to the sender and get the chonky file
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            tcp.connect((sender_ip, TCP_PORT))
        except ConnectionRefusedError:
            print("Connection refused by sender.\nThey may have closed or aren't accepting connections.\nAsk them to restart the sender.")
            return
        except OSError as e:
            print(f"Could not connect to sender: {e}\nCheck network and try again.")
            return
        else:
            print("Receiving file...")

        progress_bar = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=file_size)

        try:
            f = open("received_" + file_name, "wb")
        except PermissionError:
            print("Can't create the received file.\nCheck disk space and folder permissions.\nTry running from a different location.")
            tcp.close()
            return
        except OSError as e:
            print(f"Could not create the file: {e}\nDisk might be full or path invalid.")
            tcp.close()
            return

        received = 0
        try:
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
                if progress_bar:
                    progress_bar.update(len(chunk))
        except Exception as e:
            print(f"Transfer error: {e}\nThe sender may have closed or network dropped, or disk is full.\nAsk them to resend and check your disk space.")
        finally:
            f.close()
            if progress_bar:
                progress_bar.close()
            tcp.close()

        print(f"Saved as received_{file_name} | {received/1000000:.2f}MB")
        notification.notify(
            title="File received!",
            message="Your file has been received go check and tell me where to save it ;)",
            app_name="Fileter",
            timeout=15
        )

        SaverUI.save_with_prompt("received_" + file_name)