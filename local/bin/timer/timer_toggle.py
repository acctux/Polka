#!/usr/bin/env python3
from pathlib import Path

STATE_FILE = Path.home() / ".cache/timer_state.txt"


def toggle_pause():
    # Default to running if file doesn't exist
    if not STATE_FILE.exists():
        STATE_FILE.write_text("running")
        print("Timer started.")
        return

    state = STATE_FILE.read_text().strip()
    if state == "running":
        STATE_FILE.write_text("paused")
        print("Timer paused.")
    else:
        STATE_FILE.write_text("running")
        print("Timer resumed.")


if __name__ == "__main__":
    toggle_pause()
