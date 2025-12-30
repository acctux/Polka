#!/usr/bin/env python3
from pathlib import Path
import subprocess
import json

# ── Config ─────────────────────────────────────
DEVICE_ID = "4d76022a5910415f9073cc44af2025c3"
ICON = ""
ANDROID_MOUNT = Path.home() / "Phone" / "Internal"

CONNECTED = {
    "text": ICON,
    "tooltip": "Phone connected",
    "class": "connected",
    "alt": "connected",
}
DISCONNECTED = {
    "text": "",
    "tooltip": "Phone disconnected",
    "class": "disconnected",
    "alt": "disconnected",
}
MOUNTED = {
    "text": ICON,
    "tooltip": "Phone mounted",
    "class": "mounted",
    "alt": "mounted",
}
STATE = DISCONNECTED.copy()


def render():
    print(json.dumps(STATE), flush=True)


def is_phone_mounted():
    try:
        result = subprocess.run(
            ["findmnt", "--target", str(ANDROID_MOUNT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking mount status: {e}")
        return False


def main():
    global STATE
    new_state = DISCONNECTED
    result = subprocess.run(
        ["kdeconnect-cli", "-l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        return
    for line in result.stdout.splitlines():
        if DEVICE_ID in line:
            if "reachable" in line:
                new_state = CONNECTED
                if is_phone_mounted():
                    new_state = MOUNTED
            else:
                new_state = DISCONNECTED
            break
    if new_state != STATE:
        STATE = new_state
        render()


if __name__ == "__main__":
    main()
