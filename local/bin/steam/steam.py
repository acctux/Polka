#!/usr/bin/env python3
import json
import psutil
import sys

# === Config ===
ICON = ""
TOOLTIP = "Steam is running"


def steam_running():
    for proc in psutil.process_iter(attrs=["name"]):
        if proc.info["name"] and "steam" in proc.info["name"].lower():
            return True
    return False


def main():
    if not steam_running():
        sys.exit(0)  # Output nothing → Waybar hides the module
    output = {
        "text": ICON,
        "tooltip": TOOLTIP,
    }
    print(json.dumps(output, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
