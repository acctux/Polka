#!/usr/bin/env python3
"""
dotsync — Deploy Polka → ~/
Symlinks files + whole dirs with leading dot.
"""

import os
import shutil
import subprocess
from pathlib import Path

# ────────────────────── CONFIG ──────────────────────
dots_name = "Polka"
dest = Path.home()
skip_patterns = [
    "git",
    ".DS_Store",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
]

symlink_dirs = [
    "config/systemd/user",
    "config/nvim",
    "local/bin",
]


def log(msg: str) -> None:
    print("[Polka]", msg)


def safe_rm(path: Path) -> None:
    if path.exists():
        log(f"Remove: {path}")
        if path.is_symlink() or path.is_file():
            path.unlink(missing_ok=True)
        else:
            shutil.rmtree(path)


def safe_rm_file(path: Path) -> None:
    """Remove a file (or broken symlink) safely. Skips directories."""
    if not path.exists():
        return  # already gone

    if path.is_dir():
        log(f"Refused to remove directory: {path}")
        return

    log(f"Remove file: {path}")
    path.unlink(missing_ok=True)


def make_link(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    rel = os.path.relpath(src, dst.parent)

    try:
        if dst.is_symlink() and dst.readlink() == rel:
            return
    except OSError:
        pass

    safe_rm(dst)
    log(f"Link: {dst} → {rel}")
    dst.symlink_to(rel)


def valid_src(rel: Path, skip_patterns) -> bool:
    rel_str = rel.as_posix()
    if rel_str == ".git" or rel_str.startswith(".git/"):
        return True
    return any(rel.match(pat) for pat in skip_patterns) or any(
        rel.is_relative_to(Path(d)) for d in symlink_dirs
    )


def deploy(src: Path, dots: Path, dest: Path, skip_patterns) -> bool:
    rel = src.relative_to(dots)
    if valid_src(rel, skip_patterns):
        return False
    dst = dest / ("." + rel.as_posix())
    if dst.is_symlink() and dst.resolve(strict=False) == src.resolve():
        return False
    safe_rm_file(dest)
    make_link(src, dst)
    log(f"Linked: {dst} -> {src}")
    return True


def deploy_dir(src_dir: Path, dots: Path, dest: Path) -> bool:
    rel = src_dir.relative_to(dots)
    parts = rel.parts
    dotted_first = "." + parts[0]
    dot_path = Path(dotted_first, *parts[1:])
    dst_dir = dest / dot_path

    dst_dir.parent.mkdir(parents=True, exist_ok=True)

    if dst_dir.is_symlink() and dst_dir.resolve(strict=False) == src_dir.resolve():
        return False

    safe_rm(dst_dir)
    rel_link = os.path.relpath(src_dir, dst_dir.parent)
    dst_dir.symlink_to(rel_link)
    log(f"Linked dir: {dst_dir} → {rel_link}")
    return True


def reload_hypr() -> None:
    if shutil.which("hyprctl"):
        subprocess.run(["hyprctl", "reload"], check=False)
        log("Hyprland reloaded")


def polka(dots_name: str, dest: Path, skip_patterns: list[str]) -> None:
    dots = Path.home() / dots_name
    if not dots.is_dir():
        log(f"Error: {dots} does not exist!")
        return

    skipped = 0
    linked = 0

    # 1. Symlink whole directories
    for d in symlink_dirs:
        src = dots / d
        if src.is_dir():
            if deploy_dir(src, dots, dest):
                linked += 1
        else:
            skipped += 1

    for src in dots.rglob("*"):
        if not src.is_file():
            continue

        rel = src.relative_to(dots)
        if valid_src(rel, skip_patterns):
            skipped += 1
            continue

        if deploy(src, dots, dest, skip_patterns):
            linked += 1

    # 3. Reload + Summary
    if shutil.which("hyprctl"):
        subprocess.run(["hyprctl", "reload"], check=False)
        log("Hyprland reloaded")

    log("Deployment complete!")
    log(f"Linked: {linked} | Skipped: {skipped}")


if __name__ == "__main__":
    polka(dots_name, dest, skip_patterns)
