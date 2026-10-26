import shutil
from pathlib import Path
import Save_log

dir_path = Path.cwd()

downloads_folder = Path.home() / "Downloads"
str_downloads_folder = str(downloads_folder)

CONFIG_FILE = Path.home() / ".fileter_save_path"

def get_saved_path() -> str:
    if CONFIG_FILE.exists():
        try:
            content = CONFIG_FILE.read_text().strip()
            if content:
                return content
        except OSError:
            Save_log.enter_log("Could not read saved path config")
            print("Could not read your saved path config.\nUsing default Downloads folder instead.\nYour custom path will work again after a restart.")
        except UnicodeDecodeError:
            Save_log.enter_log("Config file corrupted")
            print("Could not read your saved path config.\nConfig file is corrupted. Using default Downloads folder.")
    return str_downloads_folder

def save_path_to_config(path: str):
    try:
        CONFIG_FILE.write_text(path)
    except OSError:
        Save_log.enter_log("Could not save path config")
        print("Could not save your preferred path.\nConfig file might be locked or read-only.\nYou'll need to re-enter the path next time.")

def save_file_to_destination(file_name, destination: str = None):

    if destination is None:
        destination = get_saved_path()
    source_file = Path(f"{str(dir_path)}/{str(file_name)}")
    destination_path = Path(destination)

    if not destination_path.is_absolute():
        destination_path = downloads_folder / destination_path

    destination_folder = destination_path
    destination_path = destination_folder / source_file.name

    try:
        destination_folder.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_file), str(destination_path))
        print(f"Saving file to {destination_folder}")
        Save_log.enter_log("File saved successfully", file_name=source_file.name, saved_path=str(destination_path))
        print(f"Successfully moved {source_file.name} to {destination_folder}")
    except FileNotFoundError:
        Save_log.enter_log("Received file not found", file_name=source_file.name)
        print("Error: The received file could not be found.")
    except PermissionError:
        Save_log.enter_log("Permission denied moving file", file_name=source_file.name, saved_path=str(destination_path))
        print("Error: You do not have permission to access the path or the folder.")
    except shutil.Error:
        Save_log.enter_log("File move failed (shutil)", file_name=source_file.name, saved_path=str(destination_path))
        print("File move failed - might be in use or cross-device.\nTry copying manually.")
    except OSError as e:
        Save_log.enter_log("OS error moving file", file_name=source_file.name, saved_path=str(destination_path))
        print(f"Something went wrong moving the file: {e}\nCheck destination folder exists and you have write access.")
