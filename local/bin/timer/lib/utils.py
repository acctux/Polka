import json
import subprocess
from datetime import timedelta
from pathlib import Path
import re

REGISTRY_FILE = Path.home() / ".config/my_timer_helper/registry.json"
SYSTEMD_USER_DIR = Path.home() / ".config/systemd/user"


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def load_registry():
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return {}


def save_registry(registry):
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2))


def list_timers():
    registry = load_registry()
    if not registry:
        print("\nNo timers found.")
        return

    print("\n📋 Your timers:")
    for name, info in registry.items():
        print(f"- {name}: runs '{info['command']}' every {info['interval']}")


def parse_interval(interval_str):
    unit_map = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
    match = re.match(r"(\d+)\s*([a-z]+)", interval_str.strip().lower())
    if not match:
        raise ValueError(f"Bad interval format: '{interval_str}'")
    num, unit = int(match.group(1)), match.group(2)[0]
    if unit not in unit_map:
        raise ValueError(f"Unsupported unit: '{unit}'")
    return timedelta(**{unit_map[unit]: num})
