#!/usr/bin/env python3
import subprocess
import json


def export_tasks():
    result = subprocess.run(
        ["task", "status:pending", "export"], capture_output=True, text=True
    )
    return json.loads(result.stdout)


def collect_pending_tasks(data):
    tasks = []
    urgent = False
    for task in data:
        description = task.get("description", "")
        urgency = float(task.get("urgency", 0))
        tasks.append((description))
        if urgency >= 7:
            urgent = True
    tasks.sort(key=lambda x: x[1], reverse=True)
    return tasks, urgent


def build_output(tasks, urgent):
    count = len(tasks)
    tooltip = f"Active:{count}\n" + "\n".join(f"•{desc}" for desc in tasks)
    output = {"text": str(count), "tooltip": tooltip}
    if count != 0:
        output["class"] = "todo"
        if urgent:
            output["class"] = "critical"
    return output


def main():
    data = export_tasks()
    tasks, urgent = collect_pending_tasks(data)
    output = build_output(tasks, urgent)
    print(json.dumps(output))


if __name__ == "__main__":
    main()
