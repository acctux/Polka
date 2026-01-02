#!/usr/bin/env python3

import subprocess
import json
import sys
import os
import re


ICON = ""


def service_active(service: str, user: bool = False) -> bool:
    cmd = ["systemctl"]
    if user:
        cmd.append("--user")
    cmd += ["is-active", "--quiet", service]
    return (
        subprocess.call(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        == 0
    )


def deluge_running() -> bool:
    return service_active("deluged.service", user=True) or service_active(
        "deluged.service", user=False
    )


def run_deluge_console() -> str | None:
    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "ignore"
    try:
        result = subprocess.run(
            ["deluge-console", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=env,
            timeout=3,
        )
        return result.stdout.strip()
    except Exception:
        return None


def clean_name(name: str) -> str:
    return re.sub(r"\s+[a-fA-F0-9]{40}$", "", name)


def parse_downloading(output: str) -> list[dict]:
    lines = output.splitlines()
    downloading = []
    current = None
    for line in lines:
        if line.startswith("["):
            raw_name = line.split("]", 1)[1].strip()
            name = clean_name(raw_name)
            current = {
                "name": name,
                "stats": "",
            }
        elif "ETA:" in line and current:
            current["stats"] = line.strip()
            eta = line.split("ETA:", 1)[1].strip()
            if eta != "-":
                downloading.append(current)
            current = None
    return downloading


def build_output(downloading: list[dict]) -> dict:
    if downloading:
        tooltip_lines = []
        for t in downloading:
            tooltip_lines.append(f"• {t['name']}")
            tooltip_lines.append(f"  {t['stats']}")

        return {
            "text": ICON,
            "tooltip": "\n".join(tooltip_lines),
            "class": "downloading",
        }

    return {
        "text": ICON,
        "tooltip": "No active downloads",
        "class": "seeding",
    }


def main() -> None:
    if not deluge_running():
        print(json.dumps({"text": ""}))
        sys.exit(0)
    output = run_deluge_console()
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
        sys.exit(0)
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
        sys.exit(0)
    downloading = parse_downloading(output)
    print(json.dumps(build_output(downloading)))


if __name__ == "__main__":
    main()

