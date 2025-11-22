#!/usr/bin/env python3
import subprocess
from pathlib import Path
import re

DURATION_FILE = Path.home() / ".cache/timer_duration.txt"
DAEMON_SCRIPT = Path.home() / "Polka/local/bin/timer/timer_daemon.py"

# Ask user for duration using a dialog box (zenity)
result = subprocess.run(
    [
        "zenity",
        "--entry",
        "--title=Countdown Timer",
        "--text=Duration (5s, 1h 5m, 1h 20m 30s, 02:09, 03:01:01, etc.",
    ],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("No duration entered. Exiting.")
    exit(1)

input_str = result.stdout.strip()
try:
    s = input_str.strip().lower()
    if any(unit in s for unit in ["h", "m", "s"]):
        duration_seconds = 0
        matches = re.findall(r"(\d+)\s*([hms])", s)
        if not matches:
            raise ValueError
        for value, unit in matches:
            value = int(value)
            if unit == "h":
                duration_seconds += value * 3600
            elif unit == "m":
                duration_seconds += value * 60
            elif unit == "s":
                duration_seconds += value
    else:
        # Otherwise fallback to previous H:M:S parsing
        parts = list(map(int, s.split(":")))
        if len(parts) == 1:
            duration_seconds = parts[0]
        elif len(parts) == 2:
            minutes, seconds = parts
            duration_seconds = minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            duration_seconds = hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError

except ValueError:
    print("Invalid input. Use formats like 1h2m3s, 10m, 90s, or H:M:S.")
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
