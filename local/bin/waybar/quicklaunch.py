#!/usr/bin/env python3
import json
import sys
import subprocess
from pathlib import Path

COMMANDS = [
    ("Mount Encrypted", "", ["kitty"]),
    ("Timer", "󱎫", ["firefox"]),
]

INDEX_FILE = Path.home() / ".cache/quicklaunch_index"
HIDE_FILE = Path.home() / ".cache/quicklaunch_hide"


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
    new = not load_hide()
    save_hide(new)
    return new


def main():
    index = load_index()
    hide = load_hide()
    for arg in sys.argv[1:]:
        if arg == "up":
            index = (index + 1) % len(COMMANDS)
            save_index(index)
        elif arg == "down":
            index = (index - 1) % len(COMMANDS)
            save_index(index)
        elif arg == "exec":
            _, _, command = COMMANDS[index]
            subprocess.Popen(command)
            return
        elif arg == "--toggle":
            hide = toggle_hide()
    label, icon, _ = COMMANDS[index]
    text = "" if hide else f" <span size='8pt'>{label}</span>"
    waybar_class = "hidden" if hide else "visible"
    print(
        json.dumps(
            {
                "text": f"{icon}{text}",
                "class": waybar_class,
                "on-click": "/home/nick/Polka/local/bin/waybar_cmd_scroll.py exec",
            }
        )
    )


if __name__ == "__main__":
    main()

