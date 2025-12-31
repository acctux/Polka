#!/usr/bin/env python3
import subprocess
import shutil
import sys
from pathlib import Path

PHONE_PATH = Path.home() / "Phone"
ANDROID_MOUNT = PHONE_PATH / "Internal"
SD_MOUNT = PHONE_PATH / "SD"
SSH_KEY = Path.home() / ".config/kdeconnect/privateKey.pem"
ANDROID_USER = "kdeconnect"
ANDROID_DIR = "/storage/emulated/0"
SD_DIR = "/storage/0000-0000"


def unmount_storage():
    for mp in [ANDROID_MOUNT, SD_MOUNT]:
        if (
            mp.exists()
            and mp.is_dir()
            and subprocess.run(["mountpoint", "-q", str(mp)]).returncode == 0
        ):
            try:
                subprocess.run(["fusermount3", "-u", str(mp)], check=True)
                print(f"Unmounted {mp}")
            except subprocess.CalledProcessError:
                print(f"Failed to unmount {mp}", file=sys.stderr)
                sys.exit(1)

    if PHONE_PATH.exists() and PHONE_PATH.is_dir():
        try:
            shutil.rmtree(PHONE_PATH)
            print(f"Removed {PHONE_PATH}")
        except Exception as e:
            print(f"Failed to remove {PHONE_PATH}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    unmount_storage()
