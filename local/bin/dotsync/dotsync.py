#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
from log import get_logger
from dot_conf import individual_items, individual_dirs, skip_patterns, dots_name

log = get_logger(dots_name)
HOME = Path.home()


def safe_remove(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
            log.info(f"Removed: {path}")
        else:
            shutil.rmtree(path)
            log.info(f"Removed tree: {path}")
    except Exception as e:
        log.warning(f"Failed to remove {path}: {e}")


def make_symlink(src: Path, dst: Path) -> bool:
    if not src.exists():
        log.error(f"Skipping missing source: {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        rel_link = os.path.relpath(src, dst.parent)
    except Exception:
        rel_link = src
    try:
        if dst.is_symlink() and dst.resolve(strict=False) == src.resolve(strict=False):
            return False
    except Exception:
        pass
    safe_remove(dst)
    try:
        dst.symlink_to(rel_link)
        log.info(f"Linked: {dst} → {rel_link}")
        return True
    except Exception as e:
        log.error(f"Failed to link {dst} → {src}: {e}")
        return False


def should_skip(rel: Path, skip_patterns) -> bool:
    rel_str = rel.as_posix()
    if rel_str == ".git" or rel_str.startswith(".git/"):
        return True
    if any(rel.match(pat) for pat in skip_patterns):
        return True
    return any(rel.is_relative_to(Path(d)) for d in individual_dirs)


def deploy_dots(dots: Path, individual_dirs, individual_items, skip_patterns) -> int:
    linked = 0
    for d in individual_dirs:
        src_dir = dots / d
        if not src_dir.is_dir():
            continue
        parts = Path(d).parts
        dotted_first = "." + parts[0]
        dot_path = Path(dotted_first, *parts[1:])
        dst_dir = HOME / ".config" / dot_path
        if make_symlink(src_dir, dst_dir):
            linked += 1
    for src in dots.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(dots)
        if should_skip(rel, skip_patterns):
            continue
        dst = HOME / ("." + rel.as_posix())
        if make_symlink(src, dst):
            linked += 1
    for item in individual_items:
        src = Path(item["src"]).expanduser()
        dest = Path(item["dest"]).expanduser()
        if make_symlink(src, dest):
            linked += 1
    return linked


def polka(
    dots_name: str,
    skip_patterns: list[str],
    individual_dirs: list[str],
    individual_items: list[dict],
) -> None:
    dots = HOME / dots_name
    if not dots.is_dir():
        log.error(f"Dotfiles directory does not exist: {dots}")
        return
    linked = deploy_dots(dots, individual_dirs, individual_items, skip_patterns)
    subprocess.run(["hyprctl", "reload"], check=False)
    log.info(f"Deployment complete! Linked: {linked}")


if __name__ == "__main__":
    polka(dots_name, skip_patterns, individual_dirs, individual_items)
