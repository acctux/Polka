#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ELAPSED_FILE = Path.home() / ".cache/timer_elapsed.txt"
DURATION_FILE = Path.home() / ".cache/timer_duration.txt"


def read_duration():
    try:
        with DURATION_FILE.open("r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def write_duration(seconds):
    with DURATION_FILE.open("w") as f:
        f.write(str(seconds))


def adjust_duration(delta):
    current = read_duration()
    if current is None:
        return
    new_duration = max(0, current + delta)
    write_duration(new_duration)


# Handle CLI adjustments (+N / -N)
if len(sys.argv) == 2:
    arg = sys.argv[1]
    if arg.startswith("+") or arg.startswith("-"):
        try:
            delta = int(arg)
            adjust_duration(delta)
        except ValueError:
            pass  # ignore invalid input

# Read remaining time
try:
    with ELAPSED_FILE.open("r") as f:
        elapsed_str = f.read().strip()
except FileNotFoundError:
    elapsed_str = ""  # fallback

# Read total timer duration for tooltip
total_seconds = read_duration()
if total_seconds is not None:
    total_td = f"{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}"
else:
    total_td = "Unknown"

waybar_output = {
    "text": f"{elapsed_str}",
    "tooltip": f"Total time: {total_td}",
    "class": "timer",
}

print(json.dumps(waybar_output))
