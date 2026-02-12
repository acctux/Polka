#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path
import sys

HOME = Path.home()
STATE_FILE = HOME / ".cache" / "hyprsunset_state"
PROFILE_DIR = HOME / ".local" / "bin" / "hyprsunset"
ACTIVE_CONF = HOME / ".config" / "hypr" / "hyprsunset.conf"


def run_cmd(cmd: list[str], check=True):
    subprocess.run(cmd, check=check, text=True)


def restart_hyprsunset():
    try:
        run_cmd(["systemctl", "--user", "restart", "hyprsunset.service"])
    except subprocess.CalledProcessError:
        run_cmd(["pkill", "-f", "hyprsunset"], check=False)
        run_cmd(["systemctl", "--user", "stop", "hyprsunset.service"], check=False)
        run_cmd(["systemctl", "--user", "start", "hyprsunset.service"])


def main():
    profiles = sorted(PROFILE_DIR.glob("*.conf"))
    if not profiles:
        sys.exit(f"No profiles found in {PROFILE_DIR}")
    if STATE_FILE.exists():
        current = int(STATE_FILE.read_text().strip())
        state = (current + 1) % len(profiles)
    else:
        state = 0
    shutil.copy2(profiles[state], ACTIVE_CONF)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(str(state))
    restart_hyprsunset()
    print(f"Applied profile: {profiles[state].name}")


if __name__ == "__main__":
    main()
