#!/usr/bin/env python3
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Tuple

CACHE = Path("/tmp/waybar-wifi.json")
ICONS = ["󰤫", "󰤯", "󰤟", "󰤢", "󰤥", "󰤨"]


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()


def safe_search(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None


def format_speed(bps: float) -> str:
    if bps < 1_000_000:
        return f"{bps / 1024:.0f}K"
    return f"{bps / 1_048_576:.1f}M"


def get_real_iface() -> str | None:
    return next(
        (p.name for p in Path("/sys/class/net").iterdir() if (p / "wireless").exists()),
        None,
    )


def get_iface() -> str | None:
    iface = run(["wg", "show", "interfaces"])
    return iface


def get_speeds(rx: int, tx: int) -> Tuple[int, int]:
    if not CACHE.exists():
        with CACHE.open("w") as f:
            json.dump({"rx": rx, "tx": tx, "t": time.time()}, f)
    prev = json.loads(CACHE.read_text())
    dt = time.time() - prev.get("t", 0)
    up_bps = (tx - prev.get("tx", 0)) / dt
    down_bps = (rx - prev.get("rx", 0)) / dt
    with CACHE.open("w") as f:
        json.dump({"rx": rx, "tx": tx, "t": time.time()}, f)
    return up_bps, down_bps


def save_counters(rx: int, tx: int) -> None:
    CACHE.write_text(json.dumps({"rx": rx, "tx": tx, "t": time.time()}))


def rssi_to_strength(rssi: int) -> int:
    if rssi >= -35:
        return 100
    if rssi <= -90:
        return 0
    strength = (rssi + 90) / 55  # -90→0%, -35→100%
    return int(strength * 100)


def main() -> None:
    iface = get_real_iface()
    if not iface:
        print('{"text":"No Wi-Fi","tooltip":"No Wi-Fi","class":"disconnected"}')
        return
    out = run(["iw", "dev", iface, "station", "dump"])
    rssi_str = safe_search(r"signal:\s+(-?\d+)", out)
    rx_str = safe_search(r"rx bytes:\s+(\d+)", out)
    tx_str = safe_search(r"tx bytes:\s+(\d+)", out)
    if not (rssi_str and rx_str and tx_str):
        print('{"text":"No data","tooltip":"No data","class":"disconnected"}')
        return
    rx = int(rx_str)
    tx = int(tx_str)
    strength = rssi_to_strength(int(rssi_str))
    icon = ICONS[min(strength // 20, len(ICONS) - 1)]
    up_bps, down_bps = get_speeds(rx, tx)
    save_counters(rx, tx)
    wg_iface = get_iface()
    if wg_iface:
        tooltip = f"{wg_iface}\n{iface}\n{strength}%\n{rssi_str}dBm\n{f'↑{format_speed(up_bps)}'}\n{f'↓{format_speed(down_bps)}'}"
        tooltip_class = "connected"
    else:
        tooltip = f"{iface}\n{strength}%\n{rssi_str}dBm\n{f'↑{format_speed(up_bps)}'}\n{f'↓{format_speed(down_bps)}'}"
        tooltip_class = "disconnected"
    print(
        json.dumps(
            {"text": icon, "tooltip": tooltip, "class": tooltip_class},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
