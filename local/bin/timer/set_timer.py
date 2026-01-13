#!/usr/bin/env python3

import json
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime, timezone

STATE_FILE = Path.home() / ".cache" / "timer_state.json"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_state(state: dict):
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(STATE_FILE)


def clear_state():
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def notify(msg: str):
    subprocess.run(["notify-send", "-a", "Timer", msg], check=False)


def format_seconds(secs: int) -> str:
    secs = max(0, int(secs))
    h, r = divmod(secs, 3600)
    m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def parse_duration(text: str) -> int:
    text = text.strip().lower()
    total = 0
    for n, u in re.findall(r"(\d+)\s*([hms])", text):
        total += int(n) * {"h": 3600, "m": 60, "s": 1}[u]
    if total == 0:
        parts = [int(x) for x in re.split(r"[:\s]+", text) if x.isdigit()]
        if len(parts) == 1:
            total = parts[0] * 60
        elif len(parts) == 2:
            total = parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            total = parts[0] * 3600 + parts[1] * 60 + parts[2]
    return max(0, total)


def default_step_for_unit() -> int:
    return 5 if get_current_unit() == "seconds" else 1


UNITS = ["minutes", "hours", "seconds"]
UNIT_MULTIPLIER = {"minutes": 60, "hours": 3600, "seconds": 1}


def get_current_unit() -> str:
    unit = load_state().get("unit")
    return unit if unit in UNITS else "minutes"


def set_unit(unit: str):
    if unit not in UNITS:
        return
    state = load_state()
    state["unit"] = unit
    save_state(state)


def cycle_unit():
    current = get_current_unit()
    idx = UNITS.index(current)
    new_unit = UNITS[(idx + 1) % 3]
    set_unit(new_unit)


def get_adjust_delta(amount_str: str) -> int:
    amount_str = amount_str.strip().lower()
    if re.match(r"^\d+\s*[hms]$", amount_str):
        return parse_duration(amount_str)
    try:
        value = int(amount_str)
    except ValueError:
        value = 1
    return value * UNIT_MULTIPLIER[get_current_unit()]


def is_running():
    s = load_state()
    return bool(s.get("start_time") and s.get("paused_at") is None)


def is_paused():
    s = load_state()
    return bool(s.get("duration") and s.get("paused_at"))


def remaining_seconds():
    s = load_state()
    if not s.get("duration"):
        return 0
    if s.get("paused_at"):
        return int(s["duration"])
    elapsed = (
        datetime.now(timezone.utc) - datetime.fromisoformat(s["start_time"])
    ).total_seconds()
    return max(0, int(s["duration"] - elapsed))


def start_timer(seconds: int):
    if seconds <= 0:
        notify("Invalid duration")
        sys.exit(1)
    now = datetime.now(timezone.utc).isoformat()
    state = load_state()
    state.update(
        {
            "duration": seconds,
            "start_time": now,
            "paused_at": None,
            "created_at": now,
            "unit": state.get("unit", "minutes"),
        }
    )
    save_state(state)
    notify(f"Started — {format_seconds(seconds)}")


def pause_timer():
    if not is_running():
        notify("Not running")
        return
    s = load_state()
    elapsed = (
        datetime.now(timezone.utc) - datetime.fromisoformat(s["start_time"])
    ).total_seconds()
    remaining = max(0, int(s["duration"] - elapsed))
    s["duration"] = remaining
    s["paused_at"] = datetime.now(timezone.utc).isoformat()
    s.pop("start_time", None)
    save_state(s)
    notify(f"Paused — {format_seconds(remaining)}")


def resume_timer():
    if not is_paused():
        notify("Not paused")
        return
    s = load_state()
    s["start_time"] = datetime.now(timezone.utc).isoformat()
    s["paused_at"] = None
    save_state(s)
    notify(f"Resumed — {format_seconds(s['duration'])}")


def toggle_pause():
    if is_running():
        pause_timer()
    elif is_paused():
        resume_timer()


def adjust_timer(delta: int):
    s = load_state()
    if not s.get("duration"):
        notify("No timer")
        sys.exit(1)
    new = max(1, s["duration"] + delta)  # never destroy
    s["duration"] = new
    clear_state()
    save_state(s)


def main():
    if len(sys.argv) == 1:
        res = subprocess.run(
            [
                "zenity",
                "--entry",
                "--width=450",
                "--title",
                "Timer",
                "--text",
                "Duration (25m, 1h30m, 90, 01:30:00)",
            ],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            sys.exit(0)
        start_timer(parse_duration(res.stdout.strip()))
        return
    arg = sys.argv[1]
    match arg:
        case "--stop":
            clear_state()
        case "--toggle":
            toggle_pause()
        case "--unit":
            if len(sys.argv) > 2:
                set_unit(
                    {"h": "hours", "m": "minutes", "s": "seconds"}.get(
                        sys.argv[2].lower(), "minutes"
                    )
                )
            else:
                cycle_unit()
        case "--up" | "--down":
            direction = 1 if arg == "--up" else -1
            if len(sys.argv) > 2:
                delta = get_adjust_delta(sys.argv[2])
            else:
                delta = default_step_for_unit() * UNIT_MULTIPLIER[get_current_unit()]
            adjust_timer(direction * delta)
        case "--status":
            get_current_unit()
            if is_running():
                print(f"RUN {format_seconds(remaining_seconds())}")
            elif is_paused():
                print(f"PAUSE {format_seconds(remaining_seconds())}")
            else:
                print("None")
        case "-t":
            start_timer(parse_duration(sys.argv[2]))
        case _:
            start_timer(parse_duration(arg))


if __name__ == "__main__":
    main()
