#!/usr/bin/env python3
import subprocess
from pathlib import Path
from conf import SERVICES

HYPRLAND_CONF = Path.home() / ".config/hypr/hyprland.conf"
INPUT_CONF = Path.home() / ".config/hypr/input.conf"

BINDINGS_TO_UNCOMMENT = [
    "bindm = SHIFT, mouse:273, movewindow",
    "bindm = SHIFT, mouse:272, resizewindow",
]


def start_user_services(SERVICES):
    for svc in SERVICES:
        try:
            subprocess.run(["systemctl", "--user", "start", svc], check=False)
            print(f"Started: {svc}")
        except Exception as e:
            print(f"Could not start {svc}: {e}")
    print("Selected user services/timers started.")


def revert_hyprland_source():
    if not HYPRLAND_CONF.exists():
        print(f"Config not found: {HYPRLAND_CONF}")
        return False
    text = HYPRLAND_CONF.read_text()
    modified = False
    if "source = gamemode.conf" in text:
        text = text.replace("source = gamemode.conf", "source = looknfeel.conf")
        modified = True
    if "# source = input.conf" in text:
        text = text.replace("# source = input.conf", "source = input.conf")
        modified = True
    if modified:
        HYPRLAND_CONF.write_text(text)
        print(f"Updated Hyprland config: {HYPRLAND_CONF}")
        return True
    else:
        print("No relevant 'source =' lines found; no change made.")
        return False


def uncomment_hypr_bindings():
    if not INPUT_CONF.exists():
        print(f"Input config not found: {INPUT_CONF}")
        return False
    changed = False
    lines = INPUT_CONF.read_text().splitlines()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if any(stripped == f"# {b}" for b in BINDINGS_TO_UNCOMMENT):
            new_lines.append(stripped[2:])  # remove '# '
            print(f"Uncommented: {stripped[2:]}")
            changed = True
        else:
            new_lines.append(line)
    if changed:
        INPUT_CONF.write_text("\n".join(new_lines) + "\n")
    return changed


def main():
    hypr_reloaded = False
    if revert_hyprland_source():
        hypr_reloaded = True
    if uncomment_hypr_bindings():
        hypr_reloaded = True
    start_user_services(SERVICES)
    if hypr_reloaded:
        subprocess.run(["hyprctl", "reload"], check=False)
        print("Hyprland reloaded.")


if __name__ == "__main__":
    main()
