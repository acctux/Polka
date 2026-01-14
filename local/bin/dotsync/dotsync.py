#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
from log import get_logger

log = get_logger("Polka")
HOME = Path.home()
CONFIG = HOME / ".config"
DOTS = HOME / "Polka"
DIRS = [
    "config/systemd/user",
    "config/nvim",
    "local/bin",
]
SEC = HOME / "Lit/Docs/base"
INDIVIDUAL_ITEMS = [
    ((SEC / "task/taskchampion.sqlite3"), (CONFIG / "task/taskchampion.sqlite3")),
    (SEC / "zsh_history", CONFIG / "zsh/.zsh_history"),
    (SEC / "fonts/calibri.ttf", CONFIG / "fonts/calibri.ttf"),
    (SEC / "fonts/calibrib.ttf", CONFIG / "fonts/calibrib.ttf"),
    (SEC / "fonts/calibrii.ttf", CONFIG / "fonts/calibrii.ttf"),
    (SEC / "fonts/calibril.ttf", CONFIG / "fonts/calibril.ttf"),
    (SEC / "fonts/calibrili.ttf", CONFIG / "fonts/calibrili.ttf"),
    (SEC / "fonts/calibriz.ttf", CONFIG / "fonts/calibriz.ttf"),
    (SEC / "fonts/times.ttf", CONFIG / "fonts/times.ttf"),
    (SEC / "fonts/timesbd.ttf", CONFIG / "fonts/timesbd.ttf"),
    (SEC / "fonts/timesbi.ttf", CONFIG / "fonts/timesbi.ttf"),
    (SEC / "fonts/timesi.ttf", CONFIG / "fonts/timesi.ttf"),
]


def safe_remove(path: Path):
    if path.exists():
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
        log.info(f"Removed: {path}")


def link_path(src: Path, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    rel_src = os.path.relpath(src, dst.parent)
    if dst.is_symlink() and dst.readlink() == Path(rel_src):
        return False
    safe_remove(dst)
    dst.symlink_to(rel_src, target_is_directory=src.is_dir())
    log.info(f"Linked: {dst} → {rel_src}")
    return True


def should_skip(rel: Path) -> bool:
    return rel.as_posix().startswith(".git") or any(
        rel.is_relative_to(Path(d)) for d in DIRS
    )


def dotted_dest(src: Path, dots: Path, dest: Path) -> Path:
    parts = src.relative_to(dots).parts
    return dest / Path("." + parts[0], *parts[1:])


def deploy_all(dots: Path, dest: Path, dirs, individual_items):
    linked = skipped = 0
    for src in dots.rglob("*"):
        if not src.is_file() or should_skip(src.relative_to(dots)):
            skipped += 1
            continue
        linked += link_path(src, dotted_dest(src, dots, dest)) or 0
    for src, dst in individual_items:
        if link_path(src.expanduser(), dst.expanduser()):
            linked += 1
        else:
            skipped += 1
    for d in dirs:
        src_dir = dots / d
        if src_dir.is_dir():
            linked += link_path(src_dir, dotted_dest(src_dir, dots, dest)) or 0
        else:
            skipped += 1
    if shutil.which("hyprctl"):
        subprocess.run(["hyprctl", "reload"], check=False)
        log.info("Hyprland reloaded")
    log.info(f"Linked: {linked} | Skipped: {skipped}")


if __name__ == "__main__":
    if not DOTS.is_dir():
        log.error(f"Error: {DOTS} does not exist!")
    else:
        deploy_all(DOTS, HOME, DIRS, INDIVIDUAL_ITEMS)
