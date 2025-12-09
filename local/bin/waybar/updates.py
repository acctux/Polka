#!/usr/bin/env python3
import subprocess
import json
import os
import time

KEYWORDS = ["linux-", "python-", "nvidia-", "fuse"]
MAX_TOOLTIP_LINES = 26


def check_lock_files():
    pacman_lock = "/var/lib/pacman/db.lck"
    checkup_lock = f"{os.getenv('TMPDIR', '/tmp')}/checkup-db-{os.getuid()}/db.lck"
    while os.path.exists(pacman_lock) or os.path.exists(checkup_lock):
        time.sleep(1)


def get_updates():
    try:
        output = subprocess.check_output(["pacman", "-Qu"], text=True)
        packages = [line.split()[0] for line in output.splitlines()]
        return packages
    except subprocess.CalledProcessError:
        return []


def generate_tooltip(packages, max_lines, keywords):
    tooltip_lines = []
    for pkg in packages:
        if any(kw in pkg for kw in keywords):
            continue
        if len(tooltip_lines) < max_lines:
            tooltip_lines.append(f"•{pkg}")
    remaining = len(packages) - len(tooltip_lines)
    if remaining > 0:
        tooltip_lines.append(f"+{remaining} more")
    return "\n".join(tooltip_lines)


def main():
    check_lock_files()
    packages = get_updates()
    total_updates = len(packages)
    if total_updates > 5:
        tooltip = generate_tooltip(packages, MAX_TOOLTIP_LINES, KEYWORDS)
        output = {"text": str(total_updates), "tooltip": tooltip}
        print(json.dumps(output))


if __name__ == "__main__":
    main()
