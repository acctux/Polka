#!/usr/bin/env python3
import json
import psutil

ICON = ""
TOOLTIP = "AyuGram is running"


def ayugram_running():
    for proc in psutil.process_iter(attrs=["name"]):
        if proc.info["name"] and "ayugram" in proc.info["name"].lower():
            return True
    return False


def main():
    if not ayugram_running():
        return
    output = {
        "text": ICON,
        "tooltip": TOOLTIP,
    }
    print(json.dumps(output, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
