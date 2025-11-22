#!/usr/bin/env python3
import subprocess
import json

urgent = False
tasks = []

result = subprocess.run(["task", "export"], capture_output=True, text=True)

try:
    data = json.loads(result.stdout)
except json.JSONDecodeError:
    print(json.dumps({"text": "!", "tooltip": "Error parsing task export"}))
    exit(1)

for task in data:
    if task.get("status") != "pending":
        continue
    description = task.get("description", "")
    urgency = float(task.get("urgency", 0))
    tasks.append((description, urgency))
    if urgency >= 9:
        urgent = True

# Sort tasks by urgency descending
tasks.sort(key=lambda x: x[1], reverse=True)

count = len(tasks)
# Add extra blank line between tasks
tooltip = f"Active: {count}\n\n" + "\n\n".join(f"•{desc}" for desc, _ in tasks)

output = {"text": str(count), "tooltip": tooltip}

if count != 0:
    if urgent:
        output["class"] = "critical"
    else:
        output["class"] = "todo"

print(json.dumps(output))
