#!/usr/bin/env python3
import subprocess
import json

urgent = False
tasks = []

# Run Taskwarrior export
result = subprocess.run(
    ["task", "export"],
    capture_output=True,
    text=True
)

try:
    data = json.loads(result.stdout)
except json.JSONDecodeError:
    print(json.dumps({"text": "!", "tooltip": "Error parsing task export"}))
    exit(1)

# Filter pending tasks and build tooltip
for task in data:
    if task.get("status") != "pending":
        continue
    description = task.get("description", "")
    urgency = float(task.get("urgency", 0))
    tasks.append((description, urgency))
    if urgency >= 9:
        urgent = True

count = len(tasks)
tooltip = f"Active tasks: {count}\n" + "\n".join(f"• {desc}" for desc, _ in tasks)

output = {
    "text": str(count),
    "tooltip": tooltip
}

if urgent:
    output["class"] = "critical"

print(json.dumps(output))

