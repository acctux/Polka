#!/usr/bin/env python3
import subprocess
from pathlib import Path

HYPRLAND_CONF = Path.home() / ".config/hypr/hyprland.conf"
INPUT_CONF = Path.home() / ".config/hypr/input.conf"

# List of user services/timers to restart
SERVICES = [
    "wall.timer",
    "emailcheck.timer",
    "hypridle.service",
    "waybar.service",
]

# Bindings to restore
BINDINGS_TO_UNCOMMENT = [
    "bindm = SHIFT, mouse:273, movewindow",
    "bindm = SHIFT, mouse:272, resizewindow",
]

def start_user_services(services):
    """Restart specific user services/timers."""
    for svc in services:
        try:
            subprocess.run(["systemctl", "--user", "start", svc], check=False)
            print(f"🚀 Started: {svc}")
        except Exception as e:
            print(f"⚠️ Could not start {svc}: {e}")
    print("✅ Selected user services/timers started.")

def revert_hyprland_source():
    """Replace 'gamemode.conf' with 'looknfeel.conf' in Hyprland config."""
    if not HYPRLAND_CONF.exists():
        print(f"❌ Config not found: {HYPRLAND_CONF}")
        return False
    
    text = HYPRLAND_CONF.read_text()
    if "source = gamemode.conf" in text:
        new_text = text.replace("source = gamemode.conf", "source = looknfeel.conf")
        HYPRLAND_CONF.write_text(new_text)
        print(f"✅ Reverted Hyprland config: gamemode → looknfeel.")
        return True
    else:
        print("⚠️ No 'source = gamemode.conf' line found; no change made.")
        return False

def uncomment_hypr_bindings():
    """Uncomment previously commented window move/resize bindings."""
    if not INPUT_CONF.exists():
        print(f"❌ Input config not found: {INPUT_CONF}")
        return False

    changed = False
    lines = INPUT_CONF.read_text().splitlines()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if any(stripped == f"# {b}" for b in BINDINGS_TO_UNCOMMENT):
            new_lines.append(stripped[2:])
            print(f"✅ Uncommented: {stripped}")
            changed = True
        else:
            new_lines.append(line)

    INPUT_CONF.write_text("\n".join(new_lines))
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
        print("🔄 Hyprland reloaded.")

if __name__ == "__main__":
    main()
