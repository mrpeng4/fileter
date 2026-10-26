import socket
import sys
import tqdm
import SaverUI
from plyer import notification
import Save_log
from pygame import mixer
import time

BROADCAST_PORT = 5000
TCP_PORT = 6000
BUFFER_SIZE = 1024
CHUNK_SIZE = 65536

def play_sound_effect():
    mixer.init()
    mixer.music.load("universfield-new-notification-017-352293.mp3")
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(0.1)

def receiver_side(device_name):
    # wait for the shout of the broadcast not someone screaming
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.settimeout(300)

    try:
        receiver.bind(("0.0.0.0", BROADCAST_PORT))
    except OSError:
        Save_log.enter_log("Port occupied error", receiver_name=device_name, port=BROADCAST_PORT)
        print("The port seems to be occupied. Please try again in a few minutes.\nThis happens because someone else is currently waiting to receive a file.\nMulti-user support is coming later, just wait for now :)")
        return
    else:
        print("Waiting for a broadcast...")
        try:
            data, addr = receiver.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            try:
                notification.notify(
                    title="File not sent!",
                    message="No receiver showed up. File not sent :(",
                    app_name="Fileter",
                    timeout=15
                )
                play_sound_effect()
            except Exception:
                print(
                    "Could not show the notification.\nYour file wasn't sent, but the notification fairy is on break.")
                receiver.close()
                return

            Save_log.enter_log("No sender found (timeout)", receiver_name=device_name)
            print("Timed out waiting for a sender.\nNo one broadcasted a file in 5 minutes.\nTry again when someone wants to send.")
            receiver.close()
            return
        receiver.close()
        Save_log.enter_log("Sender found", sender_ip=addr[0], receiver_name=device_name)

        # the message looks like: OFFER|photo.jpg|2000 This is not a sale offer
        try:
            parts = data.decode().split("|")
            file_name = parts[1]
            file_size = int(parts[2])
            sender_ip = addr[0]
            sender_name = parts[3]

        except UnicodeDecodeError:
            Save_log.enter_log("Unicode decode error", sender_ip=addr[0], receiver_name=device_name)
            print("Received a garbled message from the sender.\nTheir broadcast was corrupted. Ask them to restart and try again.")
            return
        except (IndexError, ValueError):
            Save_log.enter_log("Malformed broadcast data", sender_ip=addr[0], receiver_name=device_name)
            print("Received an incomplete message from the sender.\nThe broadcast data was malformed. Ask them to restart and try again.")
            return

        print(f"File name: {file_name}")
        print(f"File size: {file_size / 1000000:.2f}MB")
        print(f"File From: {sender_name} ({sender_ip})\n")

        print("+-----------------------------------+")
        print("| [1] Yes                           |")
        print("| [2] No                            |")
        print("+-----------------------------------+")

        try:
            user_answer = input("Do you want to receive this file: ").lower().strip()
        except (KeyboardInterrupt, EOFError):
            Save_log.enter_log("User cancelled receive prompt", receiver_name=device_name, sender_name=sender_name, sender_ip=sender_ip, file_name=file_name)
            print("\nYou exited the prompt.\nNo file received. Run the receiver again when ready.")
            return
        print("\n")

        if user_answer != "1":
            Save_log.enter_log("User declined file", receiver_name=device_name, sender_name=sender_name, sender_ip=sender_ip, file_name=file_name)
            print("No selected file not saved")
            return

        # connect to the sender and get the chonky file
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            tcp.connect((sender_ip, TCP_PORT))
            device_name_bytes = device_name.encode()
            tcp.send(device_name_bytes)
            Save_log.enter_log("Sender connected", sender_name=sender_name, sender_ip=sender_ip, receiver_name=device_name, file_name=file_name)
        except ConnectionRefusedError:
            Save_log.enter_log("Connection refused by sender", sender_ip=sender_ip, receiver_name=device_name, sender_name=sender_name, file_name=file_name)
            print("Connection refused by sender.\nThey may have closed or aren't accepting connections.\nAsk them to restart the sender.")
            return
        except OSError as e:
            Save_log.enter_log("Failed to connect to sender", sender_ip=sender_ip, receiver_name=device_name, sender_name=sender_name, file_name=file_name)
            print(f"Could not connect to sender: {e}\nCheck network and try again.")
            return
        else:
            print("Receiving file...")

        progress_bar = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=file_size, file=sys.stdout)
        tqdm.tqdm.write("[Control + C] To Cancel")

        try:
            f = open("received_" + file_name, "wb")
        except PermissionError:
            Save_log.enter_log("Permission denied creating file", receiver_name=device_name, sender_name=sender_name, sender_ip=sender_ip, file_name="received_" + file_name)
            print("Can't create the received file.\nCheck disk space and folder permissions.\nTry running from a different location.")
            tcp.close()
            return
        except OSError as e:
            Save_log.enter_log("OS error creating file", receiver_name=device_name, sender_name=sender_name, sender_ip=sender_ip, file_name="received_" + file_name)
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

        except KeyboardInterrupt:
            Save_log.enter_log("Transfer cancelled by user", receiver_name=device_name, sender_name=sender_name, sender_ip=sender_ip, file_name="received_" + file_name)
            print("\nTransfer cancelled by user.")
        except Exception as e:
            Save_log.enter_log("Transfer interrupted", receiver_name=device_name, sender_name=sender_name, sender_ip=sender_ip, file_name="received_" + file_name)
            print(f"Transfer error: {e}\nThe sender may have closed or network dropped, or disk is full.\nAsk them to resend and check your disk space.")
        finally:
            f.close()
            if progress_bar:
                progress_bar.close()
            tcp.close()

        Save_log.enter_log("File received successfully", receiver_name=device_name, sender_name=sender_name, sender_ip=sender_ip, file_name="received_" + file_name, saved_path="received_" + file_name)
        print(f"received as received_{file_name} | {received/1000000:.2f}MB")
        try:
            notification.notify(
                title="File received!",
                message="Your file has been received go check and tell me where to save it ;)",
                app_name="Fileter",
                timeout=15
            )
            play_sound_effect()
        except NotImplementedError:
            Save_log.enter_log("Notification not supported", receiver_name=device_name, sender_name=sender_name, sender_ip=sender_ip, file_name="received_" + file_name)
            print("The notification wasn't sent you, your device isn't supported for notifications :(")

        SaverUI.save_with_prompt("received_" + file_name)
        print("The path to the saved file has been copied to your clipboard")
        print("Come back later ;)")