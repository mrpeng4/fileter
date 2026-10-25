import sys
import Sender
import Receiver
import datetime

def main():
    now = datetime.datetime.now()
    readable_str = now.strftime("%B %d, %Y at %I:%M %p")
    try:
        with open("logs_file_sender.txt", "a+") as logs:
            logs.write(f"<----------{readable_str}---------->\n")
            logs.write(f"App initialized")
    except Exception:
        print("an error occurred logs weren't generated")

    print("+-----------------------------------+")
    print("| [1] Send                          |")
    print("| [2] Receive                       |")
    print("| [3] Exit                          |")
    print("+-----------------------------------+")

    print("Welcome Love to see you what do you want to do today ;)")
    try:
        user_type = input("Enter your input number: ").lower().strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye! Come back when you want to transfer files.")
        return

    if user_type == "2":
        print("You are the Receiver.\n")
        Receiver.receiver_side()

    elif user_type == "1":
        print("Tell me what do you want me to send!\n")
        Sender.sender_side()

    else:
        print("You canceled the operation.")
        print("Come back later ;)")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped")