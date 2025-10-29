#!/usr/bin/env python3
import subprocess
from pathlib import Path

HYPRLAND_CONF = Path.home() / ".config/hypr/hyprland.conf"

SERVICES = [
    "wall.timer",
    "emailcheck.timer",
    "hypridle.service",
    "waybar.service",
]


def stop_user_services(services):
    """Stop specific user services/timers without disabling them."""
    for svc in services:
        try:
            subprocess.run(["systemctl", "--user", "stop", svc], check=False)
            print(f"Stopped: {svc}")
        except Exception as e:
            print(f"Could not stop {svc}: {e}")
    print("Selected user services/timers stopped (not disabled).")


def replace_hyprland_source():
    """Replace 'looknfeel.conf' with 'gamemode.conf' in Hyprland config and comment out input.conf."""
    if not HYPRLAND_CONF.exists():
        print(f"Config not found: {HYPRLAND_CONF}")
        return

    text = HYPRLAND_CONF.read_text()

    modified = False
    if "source = looknfeel.conf" in text:
        text = text.replace("source = looknfeel.conf", "source = gamemode.conf")
        modified = True

    if "source = input.conf" in text:
        text = text.replace("source = input.conf", "# source = input.conf")
        modified = True

    if modified:
        HYPRLAND_CONF.write_text(text)
        print(f"Updated Hyprland config: {HYPRLAND_CONF}")
    else:
        print("No relevant 'source =' lines found; no change made.")


def main():
    stop_user_services(SERVICES)
    replace_hyprland_source()


if __name__ == "__main__":
    main()
