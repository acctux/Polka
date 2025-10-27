#!/usr/bin/env python3
import subprocess, json

ICON_BLACKLIST = "󱙷"
ICON_NORMAL    = ""

def get_boot_entries():
    current = "unknown"
    default = "unknown"
    try:
        result = subprocess.run(["bootctl", "status"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "Current Entry:" in line:
                current = line.split(":", 1)[1].strip()
            elif "Default Entry:" in line:
                default = line.split(":", 1)[1].strip()
    except subprocess.CalledProcessError:
        pass
    return current, default

current_boot, default_boot = get_boot_entries()

# Choose icon based on default boot
icon = ICON_BLACKLIST if "blacklist" in default_boot else ICON_NORMAL

# Tooltip shows "Reboot to apply" only if current != default
tooltip = f"Boot: {default_boot}"
if current_boot != default_boot:
    tooltip += " (Reboot to apply)"

print(json.dumps({"text": icon, "tooltip": tooltip}, ensure_ascii=False))
