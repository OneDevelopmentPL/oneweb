import os
import shutil

APP_NAME = "OneWeb"
SOURCE_FILE = "main.py"  
TARGET_DIR = os.path.expanduser("~/.local/share/MojaAplikacja")
DESKTOP_FILE_PATH = os.path.expanduser(f"~/.local/share/applications/{APP_NAME}.desktop")
ICON_PATH = ""

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)

    # Kopiowanie pliku main.py
    shutil.copy(SOURCE_FILE, TARGET_DIR)

    # Tworzenie .desktop
    exec_path = os.path.join(TARGET_DIR, SOURCE_FILE)
    desktop_content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Exec=python3 {exec_path}
Icon={ICON_PATH}
Terminal=false
Categories=Utility;Network;WebBrowser
"""

    # Zapis pliku .desktop
    with open(DESKTOP_FILE_PATH, "w") as f:
        f.write(desktop_content)

    # Nadanie uprawnień
    os.chmod(DESKTOP_FILE_PATH, 0o755)

    print("✔ Zainstalowano aplikację!")
    print(f"➜ Program skopiowany do: {TARGET_DIR}")
    print(f"➜ Plik desktop: {DESKTOP_FILE_PATH}")

if __name__ == "__main__":
    main()
