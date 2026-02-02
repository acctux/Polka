#!/usr/bin/env python3
import time
import dbus
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
FUZZEL_CONFIG = HOME / ".config/fuzzel/vpnmenu.ini"
SLEEP_TIME = 3
MAIN_CHOICES = ["WiFi", "VPN", "Cancel"]


def run_cmd(cmd, check=False, input_text=None):
    return subprocess.run(
        cmd, capture_output=True, text=True, check=check, input=input_text
    )


def run_fuzzel_menu(options, lines, config=FUZZEL_CONFIG):
    width = len(max(options, key=len)) + 1
    result = run_cmd(
        [
            "fuzzel",
            "--dmenu",
            "--hide-prompt",
            f"--width={width}",
            "--lines",
            str(lines),
            "--config",
            str(config),
        ],
        input_text="\n".join(options),
    )
    return result.stdout.strip()


class NetworkManager:
    ICONS = {
        "*\x1b[1;90m***\x1b[0m": "󰤯",
        "**\x1b[1;90m**\x1b[0m": "󰤟",
        "***\x1b[1;90m*\x1b[0m": "󰤢",
        "****": "󰤥",
    }

    def __init__(self, device_name="wlan0", sleep_time=SLEEP_TIME):
        self.device_name = device_name
        self.sleep_time = sleep_time
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(
            self.bus.get_object("net.connman.iwd", "/"),
            "org.freedesktop.DBus.ObjectManager",
        )
        self.device_path = None

    def _run_iwctl(self, cmd):
        result = subprocess.run(["iwctl"] + cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"iwctl error: {result.stderr}")
        return result.stdout

    def find_device(self):
        objs = self.manager.GetManagedObjects()
        self.device_path = next(
            (p for p, iface in objs.items() if "net.connman.iwd.Station" in iface),
            None,
        )
        if not self.device_path:
            raise Exception("No WiFi device found")

    def scan_networks(self):
        device = dbus.Interface(
            self.bus.get_object("net.connman.iwd", self.device_path),
            "net.connman.iwd.Station",
        )
        device.Scan()
        print("Scanning for networks...")
        time.sleep(self.sleep_time)

    def get_networks(self):
        return self._run_iwctl(["station", self.device_name, "get-networks"])

    def assign_icon(self, signal):
        return self.ICONS.get(signal, "")

    def filter_valid_networks(self, networks_raw: str):
        networks = []
        for line in networks_raw.splitlines():
            line = line.strip()
            if (
                "Network name" in line and "Security" in line and "Signal" in line
            ) or "------------------------------" in line:
                continue
            if "psk" in line or "WEP" in line:
                parts = line.split()
                if parts:
                    if parts[0] == "\x1b[0m":
                        if parts[1] == "\x1b[1;90m>":
                            networks.append((parts[3], parts[5]))
                        else:
                            networks.append((parts[1], parts[3]))
                    else:
                        networks.append((parts[0], parts[2]))
        networks.insert(0, ("Scan", ""))
        networks.append(("Back", ""))
        return networks

    def connect_with_zenity(self, ssid):
        if ssid in ("Back", "Scan"):
            return
        try:
            result = subprocess.run(
                ["zenity", "--password", f"--title=Enter password for {ssid}"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print("Password entry cancelled.")
                return
            password = result.stdout.strip()
        except FileNotFoundError:
            print("Zenity is not installed.")
            return
        if not password:
            print("Empty password, aborting.")
            return
        try:
            run_cmd(["iwctl", "station", self.device_name, "scan"], check=True)
            print(f"Connecting to {ssid}...")
            run_cmd(
                [
                    "iwctl",
                    "station",
                    self.device_name,
                    "connect",
                    ssid,
                    "--passphrase",
                    password,
                ],
                check=True,
            )
            print(f"Connection attempt to {ssid} started.")
        except subprocess.CalledProcessError as e:
            print(f"Connection failed: {e}")

    def run_once(self):
        self.find_device()
        raw = self.get_networks()
        networks = self.filter_valid_networks(raw)
        menu_map = {
            f"{name} {self.assign_icon(signal)}": name for name, signal in networks
        }
        options = list(menu_map.keys()) + ["Rescan"]
        choice = run_fuzzel_menu(options, len(options))

        if choice == "Rescan":
            self.scan_networks()
            return None
        return menu_map.get(choice)


def handle_wifi():
    nm = NetworkManager()
    while True:
        choice = nm.run_once()
        if choice in (None, "Back", ""):
            break
        nm.connect_with_zenity(choice)


def get_active_interfaces():
    result = run_cmd(["wg", "show"])
    return [
        line.split(":", 1)[1].strip()
        for line in result.stdout.splitlines()
        if line.startswith("interface:")
    ]


def handle_vpn():
    connections_file = Path("/run/wireguard/connections.list")
    if not connections_file.exists():
        print(f"{connections_file} does not exist.")
        sys.exit(1)
    vpns = [line.strip() for line in connections_file.read_text().splitlines() if line]
    vpns.append("Back")
    choice = run_fuzzel_menu(vpns, len(vpns))
    if choice in ("Back", ""):
        return
    for iface in get_active_interfaces():
        run_cmd(["wg-quick", "down", iface], check=True)
        print(f"Disconnected {iface}")

    run_cmd(["wg-quick", "up", choice], check=True)
    print(f"Connected to {choice}")


def main():
    while True:
        choice = run_fuzzel_menu(MAIN_CHOICES, len(MAIN_CHOICES))
        if choice == "WiFi":
            handle_wifi()
        elif choice == "VPN":
            handle_vpn()
        elif choice in ("Cancel", ""):
            sys.exit(0)


if __name__ == "__main__":
    main()
