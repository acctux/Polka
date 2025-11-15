from datetime import datetime, timedelta
import re
from utils import run, load_registry, parse_interval


def check_timer_status():
    registry = load_registry()
    if not registry:
        print("\nNo timers found.")
        return

    print("\nSelect a timer:")
    for i, name in enumerate(registry, 1):
        print(f"{i}) {name}")

    try:
        choice = int(input("Choose a number: "))
        timer_name = list(registry.keys())[choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    print(f"\n🔍 Status for '{timer_name}':")
    interval = registry[timer_name]["interval"]
    print(f"Interval: {interval}")

    out, _, _ = run(f"systemctl --user status {timer_name}.timer --no-pager")
    match = re.search(r"since (.+?);", out)
    if not match:
        print("Unable to determine last activation time.")
        return

    try:
        activated_at = datetime.strptime(
            match.group(1).strip(), "%a %Y-%m-%d %H:%M:%S %Z"
        )
    except ValueError:
        activated_at = datetime.strptime(
            match.group(1).rsplit(" ", 1)[0], "%a %Y-%m-%d %H:%M:%S"
        )

    elapsed = datetime.now() - activated_at
    try:
        interval_td = parse_interval(interval)
    except Exception:
        print("Unable to parse interval.")
        return

    remaining = interval_td - elapsed
    print(f"Time left: {max(remaining, timedelta()).seconds} seconds")
