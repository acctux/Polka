
#!/usr/bin/env python3
from pathlib import Path
import subprocess

CACHE_FILE = Path.home() / ".cache/zbar_region.png"

def main():
    try:
        region = subprocess.run(
            ["slurp"], capture_output=True, text=True, check=True
        ).stdout.strip()
        subprocess.run(
            ["grim", "-g", region, str(CACHE_FILE)], check=True
        )
        result = subprocess.run(
            ["zbarimg", "--quiet", str(CACHE_FILE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if not result:
            subprocess.run(["notify-send", "ZBar", "No code detected"])
            return
        decoded = result.split(":", 1)[1] if ":" in result else result
        subprocess.run(["wl-copy"], input=decoded.encode())
        subprocess.run(["notify-send", "ZBar", f"Copied: {decoded}"])
    except subprocess.CalledProcessError:
        subprocess.run(["notify-send", "ZBar", "Decoding failed"])
    finally:
        CACHE_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()


