#!/usr/bin/env python3
import json
import sys
import subprocess
from pathlib import Path

# -----------------------------
# TLP Commands
# -----------------------------
COMMANDS = [
    (
        "Battery",
        "󰌪",
        [
            "alacritty",
            "-e",
            "bash",
            "-c",
            "sudo",
            "python3",
            "/home/nick/Polka/local/bin/power/tlp.py",
            "batmode",
        ],
    ),
    (
        "Default",
        "",
        [
            "alacritty",
            "-e",
            "bash",
            "-c",
            "sudo python3 /home/nick/Polka/local/bin/power/tlp.py default",
        ],
    ),
    (
        "Power",
        "",
        [
            "alacritty",
            "-e",
            "bash",
            "-c",
            "sudo python3 /home/nick/Polka/local/bin/power/tlp.py none",
        ],
    ),
]

INDEX_FILE = Path.home() / ".cache/tlp_scroll_index"
STATE_FILE = Path.home() / ".cache/tlp_scroll_state"  # stores last executed mode


def load_index():
    try:
        return int(INDEX_FILE.read_text().strip())
    except Exception:
        return 0


def save_index(i):
    INDEX_FILE.write_text(str(i))


def load_state():
    try:
        return int(STATE_FILE.read_text().strip())
    except Exception:
        return None


def save_state(index):
    STATE_FILE.write_text(str(index))


# -----------------------------
# Main
# -----------------------------
def main():
    index = load_index()
    for arg in sys.argv[1:]:
        if arg == "up":
            index = (index + 1) % len(COMMANDS)
            save_index(index)
        elif arg == "down":
            index = (index - 1) % len(COMMANDS)
            save_index(index)
        elif arg == "exec":
            label, _, command = COMMANDS[index]
            subprocess.Popen(command)
            save_state(index)
            return
    label, icon, _ = COMMANDS[index]
    active_index = load_state()
    waybar_class = "active" if index == active_index else "inactive"
    text = f"{icon}"
    print(
        json.dumps(
            {
                "text": text,
                "class": waybar_class,
                "on-click": "/home/nick/Polka/local/bin/power/tlp_scroll.py exec",
            }
        )
    )


if __name__ == "__main__":
    main()
