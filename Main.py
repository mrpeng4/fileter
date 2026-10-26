import sys
import Sender
import Receiver
import datetime
import os

with open("device_name.txt", "a+") as device_name_txt:
    device_name_txt.seek(0)
    content = device_name_txt.read()
    if not content:
        device_name_user = input("Name yourself ( come on now can't you think of a name that isn't your name :| ) : ").strip()
        if device_name_user != "":
            device_name_txt.write(device_name_user)
            device_name = device_name_user
        else:
            print("How lazy can you be, at least type something pls :( ")
    else:
        device_name = content.strip()

def main():
    now = datetime.datetime.now()
    readable_str = now.strftime("%B %d, %Y at %I:%M %p")
    try:
        with open("logs_file_sender.txt", "a+") as logs:
            logs.write(f"<----------{readable_str}---------->\n")
            logs.write(f"App initialized\n")
    except Exception:
        print("an error occurred logs weren't generated")

    print("+-----------------------------------+")
    print("| [1] Send                          |")
    print("| [2] Receive                       |")
    print("| [3] Exit                          |")
    print("| [4] Logs                          |")
    print("+-----------------------------------+")

    print("Welcome Love to see you what do you want to do today ;)")
    try:
        user_type = input("Enter your input number: ").lower().strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye! Come back when you want to transfer files.")
        return

    if user_type == "2":
        print("You are the Receiver.\n")
        Receiver.receiver_side(device_name)

    elif user_type == "1":
        print("Tell me what do you want me to send!\n")
        Sender.sender_side(device_name)

    elif user_type == "4":
        os.system('cls' if os.name == 'nt' else 'clear')
        with open("logs_file_sender.txt", "r") as logs_raw:
            print(logs_raw.read())
        input("[Enter] to exit: ")
        os.system('cls' if os.name == 'nt' else 'clear')
        if __name__ == "__main__":
            try:
                main()
            except KeyboardInterrupt:
                print("\nstopped")

    else:
        print("You canceled the operation.")
        print("Come back later ;)")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped")