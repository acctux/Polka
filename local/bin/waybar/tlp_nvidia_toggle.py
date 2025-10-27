#!/usr/bin/env python3
import subprocess
import os

BOOT_ENTRY_BLACKLIST = "/boot/loader/entries/arch-blacklist-nvidia.conf"
BOOT_ENTRY_DEFAULT   = "/boot/loader/entries/arch.conf"
TLP_SNIPPET_PATH     = "/etc/tlp.d/99-battery-default.conf"

def write_tlp_snippet():
    """Create the TLP snippet to force battery mode."""
    snippet = """# Set persistent default mode to BAT (battery) always
TLP_DEFAULT_MODE=BAT
TLP_PERSISTENT_DEFAULT=1
"""
    with open(TLP_SNIPPET_PATH, "w") as f:
        f.write(snippet)

def remove_tlp_snippet():
    """Remove the TLP snippet."""
    if os.path.exists(TLP_SNIPPET_PATH):
        os.remove(TLP_SNIPPET_PATH)

def toggle_boot():
    """
    Toggle default boot based on TLP snippet existence:
    - If snippet exists → remove it, set normal boot.
    - If snippet missing → create it, set blacklist boot.
    """
    if os.path.exists(TLP_SNIPPET_PATH):
        remove_tlp_snippet()
        subprocess.run(["bootctl", "set-default", BOOT_ENTRY_DEFAULT], check=True)
    else:
        write_tlp_snippet()
        subprocess.run(["bootctl", "set-default", BOOT_ENTRY_BLACKLIST], check=True)

if __name__ == "__main__":
    toggle_boot()

