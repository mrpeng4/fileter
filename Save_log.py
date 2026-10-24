import datetime

def enter_log(message):
    now = datetime.datetime.now()
    string_time = now.strftime("%I:%M %p")
    with open("logs_file_sender.txt", "a+") as logs:
        logs.write(f"{message} :{string_time}\n")