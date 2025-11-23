#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import argparse

# Files
DURATION_FILE = Path.home() / ".cache/timer_duration.txt"
ELAPSED_FILE = Path.home() / ".cache/timer_elapsed.txt"
STATE_FILE = Path.home() / ".cache/timer_state.txt"
DEFAULT_TIME = 1
# Argument parser
parser = argparse.ArgumentParser(description="Countdown timer")
parser.add_argument("-t", "--time", type=int, help="Duration in seconds")
parser.add_argument(
    "-i",
    "--interval",
    type=int,
    help="Update interval in seconds",
    default=DEFAULT_TIME,
)
parser.add_argument("--pause", action="store_true", help="Pause the timer")
parser.add_argument("--resume", action="store_true", help="Resume the timer")
args = parser.parse_args()

INTERVAL = args.interval

# Handle pause/resume commands
if args.pause:
    STATE_FILE.write_text("paused")
    print("Timer paused.")
    exit(0)

if args.resume:
    STATE_FILE.write_text("running")
    print("Timer resumed.")
    exit(0)

# Start a new timer if duration is provided
if args.time is not None:
    total_seconds = args.time
    DURATION_FILE.write_text(str(total_seconds))
    if ELAPSED_FILE.exists():
        ELAPSED_FILE.unlink()
    STATE_FILE.write_text("running")
elif DURATION_FILE.exists():
    total_seconds = int(DURATION_FILE.read_text().strip())
    if not STATE_FILE.exists():
        STATE_FILE.write_text("running")
else:
    print("No duration set. Exiting.")
    exit(1)

start_time = datetime.now()
paused_duration = timedelta(0)
pause_start = None

while True:
    # Check current state
    state = STATE_FILE.read_text().strip() if STATE_FILE.exists() else "running"

    if state == "paused":
        if pause_start is None:
            pause_start = datetime.now()
        time.sleep(INTERVAL)
        continue
    else:
        if pause_start is not None:
            # Add paused time to total paused duration
            paused_duration += datetime.now() - pause_start
            pause_start = None

    # Re-read duration dynamically
    try:
        total_seconds = int(DURATION_FILE.read_text().strip())
    except (ValueError, FileNotFoundError):
        pass

    # Calculate remaining time
    elapsed = datetime.now() - start_time - paused_duration
    remaining_seconds = max(total_seconds - int(elapsed.total_seconds()), 0)

    if remaining_seconds == 0:
        if ELAPSED_FILE.exists():
            ELAPSED_FILE.unlink()
        subprocess.run(["notify-send", "Timer Finished", "Time's Up!"])
        break

    remaining_str = str(timedelta(seconds=remaining_seconds)).split(".")[0]

    # Update Waybar display
    with ELAPSED_FILE.open("w") as f:
        f.write(remaining_str)

    time.sleep(INTERVAL)
