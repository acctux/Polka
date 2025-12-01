#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path
from typing import List

WG_DIR = Path("/etc/wireguard")


# ─────────────────────────────────────────────────────────────
# Core helper functions
# ─────────────────────────────────────────────────────────────
def run_cmd(cmd: List[str], check: bool = False) -> subprocess.CompletedProcess:
    """Run a command and print it (verbose mode)"""
    print(f"   → Running: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def set_sysctl(key: str, value: int | str) -> bool:
    val_str = str(value)
    print(f"   sysctl → {key} = {val_str}")
    result = run_cmd(["sysctl", "-w", f"{key}={val_str}"])
    if result.returncode != 0:
        print(f"   Failed: {result.stderr.strip()}")
        return False
    return True


def get_sysctl(key: str) -> str | None:
    """Read current sysctl value"""
    result = run_cmd(["sysctl", "-n", key])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_active_interfaces() -> List[str]:
    result = run_cmd(["ip", "-brief", "link", "show", "up"])
    if result.returncode != 0:
        print("   Failed to get interface list")
        return []
    interfaces = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(maxsplit=3)
        if not parts:
            continue
        name = parts[0].split("@")[0]  # remove @parent
        interfaces.append(name)
    return interfaces


def is_proton_interface(name: str) -> bool:
    exists = (WG_DIR / f"{name}.conf").exists()
    status = "Found" if exists else "Not found"
    print(f"   Checking ProtonVPN config: {name}.conf → {status}")
    return exists


def active_proton_interfaces(
    active=[name for name in get_active_interfaces() if is_proton_interface(name)],
) -> List[str]:
    """Return only active ProtonVPN WireGuard interfaces"""
    if active:
        print(f"   Active ProtonVPN interface(s): {', '.join(active)}")
    else:
        print("   No active ProtonVPN tunnels")
    return active


# ─────────────────────────────────────────────────────────────
# IPv6 control
# ─────────────────────────────────────────────────────────────
def disable_ipv6_on_physical_interfaces(disable: bool = True) -> None:
    action = "Disabling" if disable else "Enabling"
    value = 1 if disable else 0
    print(f"\n{action} IPv6 on physical interfaces (leak protection)...")
    for name in get_active_interfaces():
        if name == "lo" or name.startswith(
            (
                "wg",
                "tun",
                "proton",
                "docker",
            )
        ):
            continue
        if is_proton_interface(name):
            continue
        set_sysctl(f"net.ipv6.conf.{name}.disable_ipv6", value)


def restart_mod(wifi_iface: str) -> None:
    run_cmd(["ip", "link", "set", wifi_iface, "down"])
    run_cmd(["ip", "link", "set", wifi_iface, "up"])


# ─────────────────────────────────────────────────────────────
# Main logic
# ─────────────────────────────────────────────────────────────
def main() -> None:
    print("ProtonVPN Toggle Script")
    print("=" * 60)
    current = active_proton_interfaces()
    if current:
        print(f"\nActive connection detected: {' '.join(current)}")
        for iface in current:
            print(f"Disconnecting {iface}...")
            run_cmd(["wg-quick", "down", iface])
            restart_mod("wlan0")
        print("Restoring IPv6 on physical interfaces...")
        disable_ipv6_on_physical_interfaces(disable=False)
        print("\nDisconnected successfully — all systems restored")
        return
    if len(sys.argv) != 2:
        print("\nNo active ProtonVPN connection.")
        return
    config = sys.argv[1]
    print(f"\nConnecting to ProtonVPN server: {config}")
    disable_ipv6_on_physical_interfaces(disable=True)
    result = run_cmd(["wg-quick", "up", config])
    if result.returncode != 0:
        print("Error output:")
        print(result.stdout or result.stderr)
        print("\nCleaning up — restoring IPv6...")
        disable_ipv6_on_physical_interfaces(disable=False)
        sys.exit(1)
    print(f"\nConnected to {config}")


if __name__ == "__main__":
    main()
