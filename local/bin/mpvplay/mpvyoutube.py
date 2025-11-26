#!/usr/bin/env python3

import subprocess
import re
import os
import sys

FLAG_FILE = "/tmp/last_mpv_url"
YOUTUBE_REGEX = re.compile(r"^https?://(www\.)?(youtube\.com/|youtu\.be/)")


def get_clipboard():
    try:
        return (
            subprocess.check_output(["wl-paste", "--no-newline"])
            .decode("utf-8")
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def main():
    clip = get_clipboard()
    if not clip or not YOUTUBE_REGEX.match(clip):
        sys.exit(0)

    last = ""
    if os.path.exists(FLAG_FILE):
        with open(FLAG_FILE, "r") as f:
            last = f.read().strip()

    if clip != last:
        with open(FLAG_FILE, "w") as f:
            f.write(clip)
        subprocess.Popen(["mpv", clip])


if __name__ == "__main__":
    main()
