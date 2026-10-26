import socket
import os
import tqdm
from plyer import notification
import Save_log
from pygame import mixer
import time
import sys

BROADCAST_PORT = 5000
TCP_PORT = 6000
CHUNK_SIZE = 65536

def play_sound_effect():
    mixer.init()
    mixer.music.load("universfield-new-notification-017-352293.mp3")
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(0.1)

def path_input():
    while True:
        user_filepath = input("provide the path of the file: ")
        try:
            file_size_bytes = os.path.getsize(user_filepath)
            file_name = os.path.basename(user_filepath)
            return file_name, file_size_bytes, user_filepath
        except FileNotFoundError:
            Save_log.enter_log("FileNotFoundError", file_path=user_filepath)

            print("That file doesn't exist at the given path.\nCheck the spelling and make sure the file is there.")
        except PermissionError:
            Save_log.enter_log("PermissionError", file_path=user_filepath)

            print("You don't have permission to access that file.\nTry running as administrator or pick a different file.")
        except IsADirectoryError:
            Save_log.enter_log("Path is directory not file", file_path=user_filepath)

            print("That's a folder, not a file.\nPlease provide the path to an actual file.")
        except OSError as e:
            Save_log.enter_log("Could not read that file", file_path=user_filepath)

            print(f"Could not read that file: {e}\nThe path might be too long or contain invalid characters.")

def sender_side(device_name):
    file_name, file_size, user_filepath = path_input()

    # UDP socket: used to shout "I have a file"
    shouter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    shouter.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # TCP socket: the begger/receiver connects here to get the chonky file
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", TCP_PORT))
    except OSError:
        Save_log.enter_log("Port occupied error", sender_name=device_name, port=TCP_PORT)
        print("The port seems to be occupied. Please try again in a few minutes.\nThis happens because someone else is currently sending a file.\nMulti-user support is coming later, just wait for now :)")
        return

    server.listen(1)

    offer = "OFFER|" + file_name + "|" + str(file_size) + "|" + device_name
    offer = offer.encode()

    print(f"File name: {file_name}")
    print(f"File size: {file_size/1000000:.2f}MB")
    print(f"File path: {user_filepath}\n")

    print("Waiting for a receiver...")
    Save_log.enter_log("Broadcasted the offer to the receivers", sender_name=device_name, file_name=file_name, file_path=user_filepath)

    end_time = time.time() + 300
    receiver_found = False
    server.settimeout(2)

    while time.time() < end_time:
        shouter.sendto(offer, ("255.255.255.255", BROADCAST_PORT))
        try:
            connection, addr = server.accept()
            receiver_name = connection.recv(1024).decode()
            receiver_found = True
            Save_log.enter_log("receiver found", receiver_name=receiver_name, receiver_ip=addr[0], file_name=file_name, sender_name=device_name)
            break
        except socket.timeout:
            pass

    if receiver_found == False:
        print("No receiver showed up. File not sent :(")

        Save_log.enter_log("No receiver showed up", sender_name=device_name, file_name=file_name)

        try:
            notification.notify(
                title="File not sent!",
                message="No receiver showed up. File not sent :(",
                app_name="Fileter",
                timeout=15
            )
            play_sound_effect()
        except Exception:
            print("Could not show the notification.\nYour file wasn't sent, but the notification fairy is on break.")
        shouter.close()
        server.close()
        return

    Save_log.enter_log("Receiver connected", receiver_name=receiver_name, receiver_ip=addr[0], file_name=file_name, sender_name=device_name)
    print(f"Receiver connected {receiver_name} ({addr[0]}),\nSending files...\n")

    # just a progress bar idk why can't i change the text color
    # it only lets me change the bar color :(
    progress_bar = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=file_size, file=sys.stdout)
    tqdm.tqdm.write("[Control + C] To Cancel")

    try:
        file = open(user_filepath, "rb")
    except FileNotFoundError:
        Save_log.enter_log("File not found for sending", sender_name=device_name, file_path=user_filepath)
        print("Can't open that file.\nEither it doesn't exist, you don't have permission, or it's a folder.\nDouble-check the path and try again.")
        shouter.close()
        server.close()
        return
    except PermissionError:
        Save_log.enter_log("Permission denied reading file", sender_name=device_name, file_path=user_filepath)
        print("You don't have permission to read that file.\nCheck file permissions or run as administrator.")
        shouter.close()
        server.close()
        return
    except IsADirectoryError:
        Save_log.enter_log("Path is directory not file", sender_name=device_name, file_path=user_filepath)
        print("That's a folder, not a file.\nPlease provide the path to an actual file.")
        shouter.close()
        server.close()
        return
    except OSError as e:
        Save_log.enter_log("OS error opening file", sender_name=device_name, file_path=user_filepath)
        print(f"Could not open the file: {e}\nThe file might be locked or the path invalid.")
        shouter.close()
        server.close()
        return

    try:
        while True:
            chunk = file.read(CHUNK_SIZE)
            if chunk == b"":
                break
            connection.sendall(chunk)
            if progress_bar:
                progress_bar.update(len(chunk))
    except (OSError, IOError, BrokenPipeError, ConnectionResetError) as e:
        Save_log.enter_log("Transfer interrupted", sender_name=device_name, receiver_name=receiver_name, receiver_ip=addr[0], file_name=file_name, file_path=user_filepath)
        print(f"Transfer interrupted: {e}\nThe receiver may have disconnected or the network hiccuped.\nTry sending again.")
    finally:
        file.close()

    connection.close()
    shouter.close()
    server.close()
    if progress_bar:
        progress_bar.close()

    Save_log.enter_log("File sent successfully", sender_name=device_name, receiver_name=receiver_name, receiver_ip=addr[0], file_name=file_name, file_path=user_filepath)
    print("Success!")
    try:
        notification.notify(
            title="File Sent!",
            message="Your file has been sent, am i cool ;)",
            app_name="fileter",
            timeout=15
        )
        play_sound_effect()
    except NotImplementedError:
        Save_log.enter_log("Notification not supported", sender_name=device_name, file_name=file_name)
        print("The notification wasn't sent you, your device isn't supported for notifications :(")
    print("Come back later ;)")