import sys
import Sender
import Receiver

def main():

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
    main()