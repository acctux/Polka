import subprocess
import logging

# ---------------- LOGGING ----------------
# Color mapping
COLORS = {
    "INFO": "\033[36m",  # cyan
    "SUCCESS": "\033[32m",  # green
    "WARNING": "\033[33m",  # yellow
    "ERROR": "\033[31m",  # red
    "RESET": "\033[0m",
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = COLORS.get(record.levelname, COLORS["RESET"])
        message = super().format(record)
        return f"{color}{message}{COLORS['RESET']}"


log = logging.getLogger("keysync")
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("[%(levelname)s] %(message)s"))
log.addHandler(handler)


# --------------- UTILITIES ----------------
def chroot_run(cmd, check=False):
    """
    Run a command inside arch-chroot /mnt and stream its output live.
    """
    chroot_cmd = ["arch-chroot", "/mnt"] + cmd
    try:
        log.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(chroot_cmd, text=True, check=check)
        log.info(f"Command finished with return code {result.returncode}")
        return result
    except subprocess.CalledProcessError as e:
        log.error(f"Command failed: {' '.join(cmd)}\nExit code: {e.returncode}")
        return e
    except OSError as e:
        log.error(f"OSError running command: {' '.join(cmd)}\n{e}")
        return None
