#!/usr/bin/env python3
from pathlib import Path
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


def is_phone_mounted():
    if not ANDROID_MOUNT.exists() or not ANDROID_MOUNT.is_dir():
        return False
    return any(p.is_dir() for p in ANDROID_MOUNT.iterdir())


def is_device_in_places(device_id: str) -> bool:
    xbel_file = Path.home() / ".local/share/user-places.xbel"
    if not xbel_file.exists():
        return False
    search_str = f"kdeconnect://{device_id}/"
    try:
        with xbel_file.open("r", encoding="utf-8") as f:
            for line in f:
                if search_str in line:
                    return True
    except Exception:
        return False
    return False


def main():
    if is_device_in_places(DEVICE_ID):
        state = CONNECTED
        if is_phone_mounted():
            state = MOUNTED
    else:
        state = DISCONNECTED
    print(json.dumps(state), flush=True)


if __name__ == "__main__":
    main()
