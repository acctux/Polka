#!/usr/bin/env python3

import json
import os
import re
import subprocess
import psutil

ICON = ""
MAX_LEN = 30


def deluge_running():
    return any(
        p.info["name"] and "deluge" in p.info["name"].lower()
        for p in psutil.process_iter(attrs=["name"])
    )


def run_console():
    try:
        return subprocess.run(
            ["deluge-console", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env={**os.environ, "PYTHONWARNINGS": "ignore"},
            timeout=3,
        ).stdout.strip()
    except Exception:
        return None


def trim(name):
    return name if len(name) <= MAX_LEN else name[: MAX_LEN - 1] + "…"


def parse(output):
    items, name = [], None
    for line in output.splitlines():
        if line.startswith("["):
            raw = re.sub(r"\s+[a-fA-F0-9]{40}$", "", line.split("]", 1)[1].strip())
            name = f"{trim(raw)}\t"
        elif name and "ETA:" in line:
            eta = line.split("ETA:", 1)[1].strip()
            if eta != "-":
                items.append((name, f"ETA: {eta}"))
            name = None
    return items


def main():
    if not deluge_running():
        print(json.dumps({"text": ""}))
        return

    output = run_console()
    if output is None:
        print(
            json.dumps(
                {
                    "text": ICON,
                    "tooltip": "Deluge is running\nUnable to query deluge-console",
                    "class": "error",
                }
            )
        )
        return

    if not output:
        print(
            json.dumps(
                {
                    "text": ICON,
                    "tooltip": "Deluge is running\nNo torrents loaded",
                    "class": "idle",
                }
            )
        )
        return

    downloads = parse(output)

    if downloads:
        tooltip = "\n".join(f"{n}\n{s}" for n, s in downloads)
        data = {"text": ICON, "tooltip": tooltip, "class": "downloading"}
    else:
        data = {"text": ICON, "tooltip": "No active downloads", "class": "seeding"}

    print(json.dumps(data))


if __name__ == "__main__":
    main()

