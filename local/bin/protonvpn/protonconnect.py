#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path
from typing import List

WG_DIR = Path("/etc/wireguard")


# ─────────────────────────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────────────────────────
def run_cmd(cmd: List[str], check: bool = False) -> subprocess.CompletedProcess:
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def get_active_interfaces() -> List[str]:
    result = run_cmd(["wg", "show"])
    if result.returncode != 0:
        print("Failed to get WireGuard interface list")
        return []
    interfaces = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("interface:"):
            iface = line.split(":", 1)[1].strip()
            interfaces.append(iface)
    return interfaces


def restart_mod(wifi_iface: str) -> None:
    run_cmd(["ip", "link", "set", wifi_iface, "down"])
    run_cmd(["ip", "link", "set", wifi_iface, "up"])


# ─────────────────────────────────────────────────────────────
# Main logic
# ─────────────────────────────────────────────────────────────
def main() -> None:
    current = [name for name in get_active_interfaces()]
    if current:
        print(f"\nActive connection detected: {' '.join(current)}")
        for iface in current:
            print(f"Disconnecting {iface}...")
            run_cmd(["wg-quick", "down", iface])
            print(f"\nDisconnected successfully from {iface}")
    if len(sys.argv) != 2:
        return
    config = sys.argv[1]
    result = run_cmd(["wg-quick", "up", config])
    if result.returncode != 0:
        print("Error output:")
        print(result.stdout or result.stderr)
        sys.exit(1)
    print(f"\nConnected to {config}")


if __name__ == "__main__":
    main()
