#!/usr/bin/env python3
import os
import re
from pathlib import Path

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
TLP_SNIPPET_PATH = "/etc/tlp.d/99-battery-save.conf"
BOOT_ENTRY_NORMAL = "arch.conf"
BOOT_ENTRY_BLACKLIST = "arch-blacklist-nvidia.conf"
WLOGOUT_LAYOUT = Path("~/.config/wlogout/layout").expanduser()
# ----------------------------------------------------------------------


def write_tlp_snippet() -> None:
    snippet = """# Set persistent default mode to BAT (battery) always
TLP_DEFAULT_MODE=BAT
TLP_PERSISTENT_DEFAULT=1
"""
    with open(TLP_SNIPPET_PATH, "w") as f:
        f.write(snippet)


def remove_tlp_snippet() -> None:
    if os.path.exists(TLP_SNIPPET_PATH):
        os.remove(TLP_SNIPPET_PATH)


def replace_wlogout_reboot(target_entry: str) -> None:
    """
    Replace --boot-loader-entry=... only in the line that contains 'reboot'
    (case-insensitive, supports 'Reboot', 'reboot', etc.)
    """
    if not WLOGOUT_LAYOUT.is_file():
        print(f"[wlogout] Layout file not found: {WLOGOUT_LAYOUT}")
        return

    lines = WLOGOUT_LAYOUT.read_text().splitlines()
    updated = False

    for i, line in enumerate(lines):
        # Look for lines that contain 'reboot' (case-insensitive) AND --boot-loader-entry=
        if re.search(r"reboot", line, re.IGNORECASE) and "--boot-loader-entry=" in line:
            new_line = re.sub(
                r'(--boot-loader-entry=)[^ \t\n"\']+', rf"\1{target_entry}", line
            )
            if new_line != line:
                lines[i] = new_line
                updated = True

    if updated:
        WLOGOUT_LAYOUT.write_text("\n".join(lines) + "\n")
        print(f"[wlogout] Updated reboot entry → {target_entry}")
    else:
        print(f"[wlogout] No matching reboot line found to update in {WLOGOUT_LAYOUT}")


def toggle_boot() -> None:
    """
    Toggle boot target based on TLP snippet:
    - If snippet exists → remove snippet, boot normal
    - If snippet missing → create it, boot blacklist
    """
    if os.path.exists(TLP_SNIPPET_PATH):
        remove_tlp_snippet()
        target_entry = BOOT_ENTRY_NORMAL
    else:
        write_tlp_snippet()
        target_entry = BOOT_ENTRY_BLACKLIST
    replace_wlogout_reboot(target_entry)


if __name__ == "__main__":
    toggle_boot()
