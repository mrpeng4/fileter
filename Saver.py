import shutil
from pathlib import Path

dir_path = Path(__file__).resolve().parent

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
            print("Could not read your saved path config.\nUsing default Downloads folder instead.\nYour custom path will work again after a restart.")
        except UnicodeDecodeError:
            print("Could not read your saved path config.\nConfig file is corrupted. Using default Downloads folder.")
    return str_downloads_folder

def save_path_to_config(path: str):
    try:
        CONFIG_FILE.write_text(path)
    except OSError:
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
        print(f"Successfully moved {source_file.name} to {destination_folder}")


    except FileNotFoundError:
        print("Error: The received file could not be found.")
    except PermissionError:
        print("Error: You do not have permission to access the path or the folder.")
    except shutil.Error:
        print("File move failed - might be in use or cross-device.\nTry copying manually.")
    except OSError as e:
        print(f"Something went wrong moving the file: {e}\nCheck destination folder exists and you have write access.")
