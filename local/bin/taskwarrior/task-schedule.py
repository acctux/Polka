#!/usr/bin/env python3
import subprocess
from datetime import date, timedelta
from typing import Optional

#############################################
# Interval-based tasks (from last added)
# Format: (description, interval_days, due_days)
#############################################
INTERVAL_TASKS = [
    ("pay credit card", 7, 3),
]

#############################################
# Exact-date tasks (recurring yearly)
# Format: (description: str, add_dates [(month, day),(month, day)], due_days)
#############################################
DATED_TASKS = [
    ("Valentines Day", [(2, 1)], 14),
    ("Anniversary", [(2, 1)], 14),
]


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(
            cmd,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return ""


def task_exists(description: str) -> bool:
    count = run(
        [
            "task",
            f"description.is:{description}",
            "status:pending",
            "count",
        ]
    )
    return int(count) > 0


def last_added_date(description: str) -> Optional[date]:
    result = run(
        [
            "task",
            f"description.is:{description}",
            "status:pending,completed",
            "limit:1",
            "rc.report.minimal.columns:entry",
            "rc.report.minimal.labels:",
            "minimal",
        ]
    )
    if not result:
        return None
    return date.fromisoformat(result.split("T")[0])


def add_task(description: str, due_days: Optional[int] = None) -> None:
    cmd = ["task", "add", description]
    if due_days is not None:
        cmd.append(f"due:{due_days}d")
    subprocess.run(
        cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def main() -> None:
    today = date.today()
    for description, interval_days, due_days in INTERVAL_TASKS:
        last = last_added_date(description)
        next_run = last + timedelta(days=interval_days) if last else today
        if next_run == today and not task_exists(description):
            add_task(description, due_days)
    for description, add_dates, due_days in DATED_TASKS:
        for month, day in add_dates:
            if (
                today.month == month
                and today.day == day
                and not task_exists(description)
            ):
                add_task(description, due_days)


if __name__ == "__main__":
    main()
