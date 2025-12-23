#!/usr/bin/env python3
import os
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

# === Config ===
NCHAT_FOLDER = "/home/nick/Lit/docs/nchat"
FOLDER = "/home/nick/Lit/docs/nchat/Telegram_+17816901633"
MAX_MESSAGES = 5
ICON = ""
HEADER_RE = re.compile(r"^(.*?) \((\d{1,2} \w{3} \d{4} \d{1,2}:\d{2})\)$")
SYSTEM_KEYWORDS = ["login code", "sticker", "call"]


def run_export():
    try:
        subprocess.run(
            ["/usr/bin/nchat", "--export", NCHAT_FOLDER],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def parse_file(path):
    messages = []
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    i = 0
    while i < len(lines):
        match = HEADER_RE.match(lines[i])
        if match:
            name = match.group(1)
            ts_str = match.group(2)
            try:
                ts = datetime.strptime(ts_str, "%d %b %Y %H:%M")
            except ValueError:
                i += 1
                continue
            i += 1
            body_lines = []
            while i < len(lines) and not HEADER_RE.match(lines[i]):
                if lines[i].strip():
                    body_lines.append(lines[i])
                i += 1
            body = "\n".join(body_lines).strip()
            if not any(k.lower() in body.lower() for k in SYSTEM_KEYWORDS):
                messages.append({"sender": name, "timestamp": ts, "message": body})
        else:
            i += 1
    return messages


def main():
    run_export()
    all_messages = []
    if Path(FOLDER).exists():
        for fname in os.listdir(FOLDER):
            if fname.endswith(".txt"):
                all_messages.extend(parse_file(os.path.join(FOLDER, fname)))
    all_messages.sort(key=lambda m: m["timestamp"], reverse=True)
    latest = all_messages[:MAX_MESSAGES]
    if latest:
        tooltip_lines = []
        for m in latest:
            msg = m["message"]
            if len(msg) > 50:
                msg = msg[:50].rstrip() + "…"
            tooltip_lines.append(f"• {m['sender']}: {msg}")
        tooltip = "\n\n".join(tooltip_lines)
    else:
        tooltip = "No messages"
    output = {
        "text": ICON,
        "tooltip": tooltip,
    }
    print(json.dumps(output, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
