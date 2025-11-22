#!/usr/bin/env python3
import subprocess
import json

urgent = False
tasks = []

# Run: task export
result = subprocess.run(["task", "export"], capture_output=True, text=True)

try:
    data = json.loads(result.stdout)
except json.JSONDecodeError:
    subprocess.run(["notify-send", "Task Reminder", "Error parsing task export"])
    exit(1)

for task in data:
    if task.get("status") != "pending":
        continue

    description = task.get("description", "")
    urgency = float(task.get("urgency", 0))

    tasks.append((description, urgency))

    if urgency >= 9:
        urgent = True

# Sort tasks by urgency
tasks.sort(key=lambda x: x[1], reverse=True)

count = len(tasks)

if count == 0:
    body = "You have no pending tasks."
else:
    body = "\n".join(f"• {desc}" for desc, _ in tasks)

urgency_flag = "critical" if urgent else "normal"

subprocess.run(
    [
        "notify-send",
        "--urgency=" + urgency_flag,
        "To-Do Reminder",
        body,
    ]
)
