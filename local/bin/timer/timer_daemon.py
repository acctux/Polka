#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
from pathlib import Path

# Files
DURATION_FILE = Path.home() / ".cache/timer_duration.txt"
ELAPSED_FILE = Path.home() / ".cache/timer_elapsed.txt"

INTERVAL = 5  # seconds between updates

# Read initial duration
if DURATION_FILE.exists():
    with DURATION_FILE.open("r") as f:
        total_seconds = int(f.read().strip())
else:
    print("No duration set. Exiting.")
    exit(1)

start_time = datetime.now()

while True:
    # Re-read duration dynamically
    try:
        with DURATION_FILE.open("r") as f:
            total_seconds = int(f.read().strip())
    except (ValueError, FileNotFoundError):
        pass

    # Calculate remaining time
    elapsed = datetime.now() - start_time
    remaining_seconds = max(total_seconds - int(elapsed.total_seconds()), 0)

    if remaining_seconds == 0:
        if ELAPSED_FILE.exists():
            ELAPSED_FILE.unlink()  # clear file at 0
        break

    # Format remaining time
    remaining_td = timedelta(seconds=remaining_seconds)
    remaining_str = str(remaining_td).split(".")[0]  # HH:MM:SS

    # Write plain text for Waybar
    with ELAPSED_FILE.open("w") as f:
        f.write(remaining_str)

    time.sleep(INTERVAL)
