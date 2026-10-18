import Sender
import Receiver

print("Welcome Love to see you what do you want to do today ;)")
user_type = input("Enter \"r\" to receive or \"s\" to send: ").lower().strip()

if user_type == "r":
    print("You are the Receiver.\n")
    Receiver.receiver_side()

elif user_type == "s":
    print("You are the Sender.\n")
    Sender.sender_side()

else:
    print("You canceled the operation.")
    print("Come back later ;)")
