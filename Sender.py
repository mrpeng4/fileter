import socket
import time
import os
import tqdm
from plyer import notification

BROADCAST_PORT = 5000
TCP_PORT = 6000
CHUNK_SIZE = 65536

def path_input():
    while True:
        user_filepath = input("provide the path of the file: ")
        try:
            file_size_bytes = os.path.getsize(user_filepath)
            file_name = os.path.basename(user_filepath)
            return file_name, file_size_bytes, user_filepath
        except FileNotFoundError:
            print("That file doesn't exist at the given path.\nCheck the spelling and make sure the file is there.")
        except PermissionError:
            print("You don't have permission to access that file.\nTry running as administrator or pick a different file.")
        except IsADirectoryError:
            print("That's a folder, not a file.\nPlease provide the path to an actual file.")
        except OSError as e:
            print(f"Could not read that file: {e}\nThe path might be too long or contain invalid characters.")

def sender_side():
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
        print("The port seems to be occupied. Please try again in a few minutes.\nThis happens because someone else is currently sending a file.\nMulti-user support is coming later, just wait for now :)")
        return

    server.listen(2)

    offer = "OFFER|" + file_name + "|" + str(file_size)
    offer = offer.encode()

    print(f"File name: {file_name}")
    print(f"File size: {file_size/1000000:.2f}MB")
    print(f"File path: {user_filepath}\n")

    print("Waiting for a receiver...")
    end_time = time.time() + 300
    receiver_found = False
    server.settimeout(2)

    while time.time() < end_time:
        shouter.sendto(offer, ("255.255.255.255", BROADCAST_PORT))
        try:
            connection, addr = server.accept()
            receiver_found = True
            break
        except socket.timeout:
            pass

    if receiver_found == False:
        print("No receiver showed up. File not sent :(")
        try:
            notification.notify(
                title="File not sent!",
                message="No receiver showed up. File not sent :(",
                app_name="Fileter",
                timeout=15
            )
        except Exception:
            print("Could not show the notification.\nYour file wasn't sent, but the notification fairy is on break.")
        shouter.close()
        server.close()
        return

    print(f"Receiver connected {addr[0]},\nSending files...\n")

    # just a progress bar idk why can't i change the text color
    # it only lets me change the bar color :(
    progress_bar = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=file_size)
    print("[Control + C] To Cancel")

    try:
        file = open(user_filepath, "rb")
    except FileNotFoundError:
        print("Can't open that file.\nEither it doesn't exist, you don't have permission, or it's a folder.\nDouble-check the path and try again.")
        shouter.close()
        server.close()
        return
    except PermissionError:
        print("You don't have permission to read that file.\nCheck file permissions or run as administrator.")
        shouter.close()
        server.close()
        return
    except IsADirectoryError:
        print("That's a folder, not a file.\nPlease provide the path to an actual file.")
        shouter.close()
        server.close()
        return
    except OSError as e:
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
        print(f"Transfer interrupted: {e}\nThe receiver may have disconnected or the network hiccuped.\nTry sending again.")
    finally:
        file.close()

    connection.close()
    shouter.close()
    server.close()
    if progress_bar:
        progress_bar.close()

    print("Success!")
    try:
        notification.notify(
            title="File Sent!",
            message="Your file has been sent, am i cool ;)",
            app_name="fileter",
            timeout=15
        )
    except NotImplementedError:
        print("The notification wasn't sent you, your device isn't supported for notifications :(")
    print("Come back later ;)")