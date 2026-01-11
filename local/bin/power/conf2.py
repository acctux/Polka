#!/usr/bin/env python3
import sys
from pathlib import Path

HYPRLAND_CONF = Path.home() / ".config/hypr/power.conf"

OPTION_LOW = """\
monitor=,1920x1080@60,auto,1
# exec=sleep 1 && pkill swww && swww-daemon
animations {
    enabled=0
}
"""

OPTION_HIGH = """\
monitor=,1920x1080@144,auto,1
"""


def write_conf(content: str):
    try:
        with open(HYPRLAND_CONF, "w") as f:
            f.write(content)
        print(f"Wrote {HYPRLAND_CONF}")
    except PermissionError:
        print(f"Permission denied: cannot write {HYPRLAND_CONF}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} {{batmode|default|none}}")
        sys.exit(1)

    mode = sys.argv[1]

    # Set Hyprland config based on mode
    if mode == "batmode":
        write_conf(OPTION_LOW)
    else:
        write_conf(OPTION_HIGH)


if __name__ == "__main__":
    main()

