from pathlib import Path
import Saver
import Save_log
import pyperclip

def save_with_prompt(file_name: str):
    print("Where do you want to save the file?\n")
    print("+-------------------------------------------------------------------+")
    print("| [y] Yes (Save in the download or the folder you have registered)  |")
    print("| [c] Change (Set a folder to save the file in)                     |")
    print("| [d] Delete (Do not save the file and delete it)                   |")
    print("+-------------------------------------------------------------------+")
    try:
        saver_input = input("Choice (y/c/d): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nYou exited the save menu.\nFile left in current folder. Move it manually if needed.")
        return

    if saver_input == "c":
        new_path = settings_submenu()
        if new_path:
            Saver.save_path_to_config(new_path)
            Save_log.enter_log("Changed the path", saved_path=new_path)
            Saver.save_file_to_destination(file_name, new_path)
            pyperclip.copy(new_path)
            Save_log.enter_log("File saved", file_name=file_name, saved_path=new_path)
        else:
            Saver.save_file_to_destination(file_name)
            Save_log.enter_log("File saved to Downloads", file_name=file_name, saved_path=Saver.get_saved_path())
    elif saver_input == "y":
        saved_path = Saver.get_saved_path()
        Saver.save_file_to_destination(file_name, saved_path)
        pyperclip.copy(saved_path)
        Save_log.enter_log("File saved", file_name=file_name, saved_path=saved_path)
    elif saver_input == "d":

        print("Deleting file...")
        source_file = Saver.dir_path / file_name
        try:
            if source_file.exists():
                source_file.unlink()
                print(f"Deleted Successfully: {file_name}")
                Save_log.enter_log("File deleted", file_name=file_name)
                print("Come back later ;)")
            else:
                print("File not found, nothing to delete.")
                Save_log.enter_log("File not found, nothing to delete.", file_name=file_name)
                print("Come back later ;)")
        except PermissionError:
            print("Could not delete the file.\nIt might be open elsewhere or read-only.\nDelete it manually later.")
            Save_log.enter_log("Could not delete the file", file_name=file_name)
        except OSError as e:
            print(f"Could not delete the file: {e}\nDelete it manually later.")
            Save_log.enter_log(f"Could not delete the file: {e}", file_name=file_name)
    else:
        print("Invalid choice. Saving to default location.")
        Saver.save_file_to_destination(file_name)


def settings_submenu() -> str | None:
    while True:
        current = Saver.get_saved_path()
        print(f"\nCurrent save path: {current}")
        try:
            path = input("Enter new save path (relative to Downloads or absolute, empty to cancel): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            return None
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
        except PermissionError:
            print("Could not create that folder.\nYou don't have permission. Try a different location.")
        except OSError as e:
            print(f"Could not create that folder: {e}\nCheck the path is valid and you have permission.\nTry a simpler path like 'MyFiles'.")