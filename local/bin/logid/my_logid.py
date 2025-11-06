#!/usr/bin/env python3
import re
import time
import subprocess
from pathlib import Path

DEVICE = "MX Master 3S"
LOG = Path.home() / ".cache" / "logid_check.log"
ATTEMPTS = 3
LOGID_DELAY = 4
MAIN_DELAY = 20


def log_it(message: str):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%F %T')}  {message}\n")


def restart_logid():
    log_it("Restarting logid...")
    result = subprocess.run(
        ["sudo", "logid", "restart"], capture_output=True, text=True
    )
    LOG.write_text(result.stdout + result.stderr)
    time.sleep(LOGID_DELAY)


def log_contains(pattern: str) -> bool:
    if not LOG.exists():
        return False
    with open(LOG, "r") as f:
        return re.search(pattern, f.read(), re.MULTILINE) is not None


def restart_logic():
    if log_contains(DEVICE):
        if not log_contains(r"disconnected|Failed|Error|Failure"):
            log_it("Found device and no errors.")
            return True
        else:
            log_it("Errors detected, restarting logid.")
            restart_logid()
    else:
        log_it("Device not found, restarting logid.")
        restart_logid()
    return False


def run_attempts():
    for i in range(1, ATTEMPTS + 1):
        log_it(f"Attempt {i}/{ATTEMPTS}")
        restart_logic()
        pid = get_logid_pid()
        if pid:
            log_it(f"logid PID: {pid}")
        else:
            log_it("logid not running.")
        time.sleep(LOGID_DELAY)


def get_logid_pid():
    try:
        pid_output = subprocess.check_output(["pgrep", "-x", "logid"], text=True)
        return pid_output.strip()
    except subprocess.CalledProcessError:
        return None


def main():
    if LOG.exists():
        LOG.unlink()

    while True:
        run_attempts()
        pid = get_logid_pid()
        if pid:
            log_it(f"logid running with PID {pid}")
        else:
            log_it("logid process missing, restarting.")
            restart_logid()

        time.sleep(MAIN_DELAY)


if __name__ == "__main__":
    main()
