#!/usr/bin/env python3

import json
import subprocess
import psutil
import re
import os

ICON = ""
MAX_LEN = 30


def trim(name):
    return name if len(name) <= MAX_LEN else name[: MAX_LEN - 1] + "…"


def deluge_info():
    if not any(
        "deluge" in (p.info["name"] or "").lower()
        for p in psutil.process_iter(attrs=["name"])
    ):
        return None
    try:
        return subprocess.run(
            ["deluge-console", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env={**os.environ, "PYTHONWARNINGS": "ignore"},
            timeout=3,
        ).stdout
    except Exception:
        return None


def parse_downloads(output):
    downloads, name = [], None
    for line in output.splitlines():
        if line.startswith("["):
            raw = re.sub(r"\s+[a-fA-F0-9]{40}$", "", line.split("]", 1)[1].strip())
            name = f"{trim(raw)}\t"
        elif name and "ETA:" in line:
            eta = line.split("ETA:", 1)[1].strip()
            if eta != "-":
                downloads.append((name, f"ETA: {eta}"))
            name = None
    return downloads


def main():
    output = deluge_info()
    if output is None:
        print(json.dumps({"text": ""}))
        return
    downloads = parse_downloads(output)
    if downloads:
        tooltip = "\n".join(f"{n}\n{s}" for n, s in downloads)
        data = {"text": ICON, "tooltip": tooltip, "class": "downloading"}
    else:
        data = {
            "text": ICON,
            "tooltip": "No active downloads",
            "class": "seeding" if "Deluge" in output else "idle",
        }
    print(json.dumps(data))


if __name__ == "__main__":
    main()

