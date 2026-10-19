from pathlib import Path
import Saver

def save_with_prompt(file_name: str):
    print("Where do you want to save the file?\n")
    print("+-------------------------------------------------------------------+")
    print("| [y] Yes (Save in the download or the folder you have registered)  |")
    print("| [c] Change (Set a folder to save the file in)                     |")
    print("| [d] Delete (Do not save the file and delete it)                   |")
    print("+-------------------------------------------------------------------+")
    saver_input = input("Choice (y/c/d): ").strip().lower()

    if saver_input == "c":
        new_path = settings_submenu()
        if new_path:
            Saver.save_path_to_config(new_path)
            Saver.save_file_to_destination(file_name, new_path)
        else:
            Saver.save_file_to_destination(file_name)
    elif saver_input == "y":
        Saver.save_file_to_destination(file_name)
    elif saver_input == "d":
        source_file = Saver.dir_path / file_name
        if source_file.exists():
            source_file.unlink()
            print(f"Deleted Successfully: {file_name}")
            print("Come back later ;)")
        else:
            print("File not found, nothing to delete.")
            print("Come back later ;)")
    else:
        print("Invalid choice. Saving to default location.")
        Saver.save_file_to_destination(file_name)


def settings_submenu() -> str | None:
    while True:
        current = Saver.get_saved_path()
        print(f"\nCurrent save path: {current}")
        path = input("Enter new save path (relative to Downloads or absolute, empty to cancel): ").strip()
        if not path:
            print("Cancelled.")
            return None
        full_path = Path(path)
        if not full_path.is_absolute():
            full_path = Saver.downloads_folder / full_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"Path set to: {full_path}")
            return str(full_path)
        except Exception as e:
            print(f"Invalid path: {e}. Try again.")