import datetime

def enter_log(message, sender_name=None, receiver_name=None, file_name=None,
              file_path=None, sender_ip=None, receiver_ip=None, saved_path=None,
              port=None):
    now = datetime.datetime.now()
    string_time = now.strftime("%I:%M %p")
    parts = [f"[{message}]"]
    if sender_name is not None:
        parts.append(f"sender={sender_name}")
    if receiver_name is not None:
        parts.append(f"receiver={receiver_name}")
    if file_name is not None:
        parts.append(f"file={file_name}")
    if file_path is not None:
        parts.append(f"path={file_path}")
    if sender_ip is not None:
        parts.append(f"sender_ip={sender_ip}")
    if receiver_ip is not None:
        parts.append(f"receiver_ip={receiver_ip}")
    if saved_path is not None:
        parts.append(f"saved_path={saved_path}")
    if port is not None:
        parts.append(f"port={port}")
    line = " | ".join(parts) + f" :{string_time}\n"
    with open("logs_file_sender.txt", "a+") as logs:
        logs.write(line)
