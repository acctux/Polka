#!/usr/bin/env python3
import json
import psutil
import subprocess
from pathlib import Path

INTERVAL = 5
CACHE_FILE = Path("/tmp/waybar-wifi-counters.json")
WIFI_ICONS = ["󰤫", "󰤯", "󰤟", "󰤢", "󰤥", "󰤨"]  # 0%, 1–19, 20–39, 40–59, 60–79, 80–100%


# ─── Helpers ───
def run(cmd):
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=4
        ).strip()
    except:
        return None


def load_prev():
    return json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}


def save_prev(data):
    CACHE_FILE.write_text(json.dumps(data))


def human_bytes(b):
    for unit in ["B", "K", "M", "G"]:
        if b < 1024:
            return f"{b:.0f}{unit}"
        b /= 1024
    return f"{b:.1f}T"


def get_iface():
    out = run(["ip", "-o", "route", "get", "8.8.8.8"])
    return out.split("dev", 1)[1].split()[0] if out and "dev" in out else None


def get_wifi_strength():
    out = run(["nmcli", "-t", "-f", "ACTIVE,SIGNAL", "dev", "wifi"])
    if not out:
        return 0
    for line in out.splitlines():
        if line.startswith("yes:"):
            return int(line.split(":", 1)[1])
    return 0


def get_speed(iface, prev):
    if not iface:
        return 0, 0
    io = psutil.net_io_counters(pernic=True).get(iface)
    if not io:
        return 0, 0
    sent, recv = io.bytes_sent, io.bytes_recv
    old = prev.get(iface, {"sent": sent, "recv": recv})
    up = max(0, (sent - old["sent"]) // INTERVAL)
    down = max(0, (recv - old["recv"]) // INTERVAL)
    prev[iface] = {"sent": sent, "recv": recv}
    return up, down


def get_firewalld_zone():
    """
    Returns just the zone name without ' (default)'
    Examples:
        "block (default)\n..." → "block"
        "home\n..."           → "home"
        no firewalld / error  → "off"
    """
    output = run(["firewall-cmd", "--get-active-zones"])
    if not output:
        return "off"

    first_line = output.splitlines()[0]  # e.g. "block (default)" or "home"
    zone_name = first_line.split(None, 1)[0]  # take everything before first space
    return zone_name


# ─── Main ───
prev = load_prev()
iface = get_iface() or "—"
strength = get_wifi_strength()
up, down = get_speed(iface, prev)
zone = f"{get_firewalld_zone()}󱨑"
cls = "vpn" if iface.startswith(("proton", "tun", "wg", "tail")) else "wifi"

# Icon selection
icon = WIFI_ICONS[0] if strength == 0 else WIFI_ICONS[(strength - 1) // 20 + 1]

# Output
if strength == 0:
    text = f"{icon} {iface}"
    tooltip = "No Wi-Fi connection"
    cls = "disconnected"
else:
    text = icon
    tooltip = f"{icon} {iface}\n{strength}%\n↑{human_bytes(up)}\n↓{human_bytes(down)}\n{zone}\n"

save_prev(prev)
print(json.dumps({"text": text, "tooltip": tooltip, "class": cls}, ensure_ascii=False))
