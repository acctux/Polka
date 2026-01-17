#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path
import sys

HOME = Path.home()
STATE_FILE = HOME / ".cache" / "hyprsunset_state"
PROFILE_DIR = HOME / "Polka" / "local" / "bin" / "hyprsunset"
ACTIVE_CONF = HOME / ".config" / "hypr" / "hyprsunset.conf"


def get_profiles(directory: Path):
    profiles = sorted(directory.glob("*.conf"))
    if not profiles:
        sys.exit(f"No profiles found in {directory}")
    return profiles


def load_state(file: Path, max_index: int) -> int:
    if file.exists():
        try:
            return (int(file.read_text().strip()) + 1) % (max_index + 1)
        except ValueError:
            pass
    return 0


def save_state(file: Path, state: int):
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(str(state))


def apply_profile(profile: Path):
    shutil.copy2(profile, ACTIVE_CONF)


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
    profiles = get_profiles(PROFILE_DIR)
    state = load_state(STATE_FILE, len(profiles) - 1)
    apply_profile(profiles[state])
    save_state(STATE_FILE, state)
    restart_hyprsunset()
    print(f"Applied profile: {profiles[state].name}")


if __name__ == "__main__":
    main()
