import shutil
from pathlib import Path

dir_path = Path(__file__).resolve().parent

downloads_folder = Path.home() / "Downloads"
str_downloads_folder = str(downloads_folder)

CONFIG_FILE = Path.home() / ".fileter_save_path"

def get_saved_path() -> str:
    if CONFIG_FILE.exists():
        content = CONFIG_FILE.read_text().strip()
        if content:
            return content
    return str_downloads_folder

def save_path_to_config(path: str):
    CONFIG_FILE.write_text(path)

def save_file_to_destination(file_name, destination: str = None):

    if destination is None:
        destination = get_saved_path()

    # 1. Define your paths using Path objects (works natively on Windows, Mac, Linux)
    source_file = Path(f"{str(dir_path)}/{str(file_name)}")
    destination_path = Path(destination)

    # If relative path, make it relative to Downloads folder
    if not destination_path.is_absolute():
        destination_path = downloads_folder / destination_path

    destination_folder = destination_path

    # 2. Construct the full destination path (keeping the same file name)
    destination_path = destination_folder / source_file.name

    # 3. Safely move the file
    try:
        # Ensure the destination folder actually exists before moving
        destination_folder.mkdir(parents=True, exist_ok=True)

        # Move the file
        shutil.move(str(source_file), str(destination_path))
        print(f"Successfully moved {source_file.name} to {destination_folder}")

    except FileNotFoundError:
        print("Error: The source file could not be found.")
    except PermissionError:
        print("Error: You do not have permission to access one of the paths.")
