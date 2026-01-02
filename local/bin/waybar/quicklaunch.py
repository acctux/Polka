#!/usr/bin/env python3
import json
import sys
import subprocess
from pathlib import Path

FOLDERS = [
    ("/home/nick/Documents", "󱧶"),
    ("/home/nick/Documents/Decrypted", "󰉑"),
    ("/home/nick/Polka", "󱂵"),
    ("/home/nick/Lit/noah", "󰉒"),
    ("/etc", "󱂀"),
    ("/usr/local/bin", "󱁿"),
]
INDEX_FILE = Path.home() / ".cache/nemo_scroll_index"
HIDE_FILE = Path.home() / ".cache/nemo_scroll_hide"


def load_index():
    try:
        return int(INDEX_FILE.read_text().strip())
    except Exception:
        return 0


def save_index(i):
    INDEX_FILE.write_text(str(i))


def load_hide():
    try:
        return HIDE_FILE.read_text().strip() == "1"
    except Exception:
        return False


def save_hide(value: bool):
    HIDE_FILE.write_text("1" if value else "0")


def toggle_hide():
    current = load_hide()
    new = not current
    save_hide(new)
    return new


def main():
    index = load_index()
    hide = load_hide()
    for arg in sys.argv[1:]:
        if arg == "up":
            index = (index + 1) % len(FOLDERS)
            save_index(index)
        elif arg == "down":
            index = (index - 1) % len(FOLDERS)
            save_index(index)
        elif arg == "exec":
            folder, _ = FOLDERS[index]
            subprocess.Popen(["nemo", folder])
            return
        elif arg == "--toggle":
            hide = toggle_hide()
    folder, icon = FOLDERS[index]
    folder_name = f" {Path(folder).name}"
    if hide:
        folder_name = ""
    waybar_class = "hidden" if hide else "visible"
    print(
        json.dumps(
            {
                "text": f"{icon}<span size='8pt'>{folder_name}</span>",
                "class": waybar_class,
                "on-click": "/home/nick/Polka/local/bin/folders/nemo_scroll.py exec",
            }
        )
    )


if __name__ == "__main__":
    main()
