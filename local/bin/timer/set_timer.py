#!/usr/bin/env python3
import subprocess
from pathlib import Path

DURATION_FILE = Path.home() / ".cache/timer_duration.txt"
DAEMON_SCRIPT = Path.home() / "Polka/local/bin/timer/timer_daemon.py"

# Ask user for duration using a dialog box (zenity)
result = subprocess.run(
    [
        "zenity",
        "--entry",
        "--title=Countdown Timer",
        "--text=Enter duration (HH:MM) or seconds:",
    ],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("No duration entered. Exiting.")
    exit(1)

input_str = result.stdout.strip()

# Parse HH:MM
try:
    if ":" in input_str:
        hours, minutes = map(int, input_str.split(":"))
        duration_seconds = hours * 3600 + minutes * 60
    else:
        # fallback: just seconds
        duration_seconds = int(input_str)
except ValueError:
    print("Invalid input. Enter HH:MM or number of seconds.")
    exit(1)

# Write duration to file
with DURATION_FILE.open("w") as f:
    f.write(str(duration_seconds))

# Stop existing daemon (if any)
subprocess.run(
    ["pkill", "-f", str(DAEMON_SCRIPT)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Start the daemon
subprocess.Popen([str(DAEMON_SCRIPT)])
print(f"Timer started for {duration_seconds} seconds")
