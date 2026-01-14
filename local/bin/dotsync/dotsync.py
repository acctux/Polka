#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
from log import get_logger

log = get_logger("Polka")
HOME = Path.home()
CONFIG_DIR = HOME / ".config"
SHARE_DIR = HOME / ".local" / "share"
DOTFILES_DIR = HOME / "Polka"
DIRECTORIES_TO_LINK = [
    "config/systemd/user",
    "config/nvim",
    "local/bin",
]
BASE_DIR = HOME / "Lit/Docs/base"
INDIVIDUAL_DIRS = [
    (BASE_DIR / "fonts", SHARE_DIR / "fonts"),
    (BASE_DIR / "task", CONFIG_DIR / "task"),
    (BASE_DIR / "zsh", CONFIG_DIR / "zsh"),
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
    relative_src = os.path.relpath(src, dst.parent)
    if dst.is_symlink() and dst.readlink() == Path(relative_src):
        return False
    safe_remove(dst)
    dst.symlink_to(relative_src, target_is_directory=src.is_dir())
    log.info(f"Linked: {dst} → {relative_src}")
    return True


def should_skip(rel_path: Path, directories_to_link) -> bool:
    if rel_path.as_posix().startswith(".git"):
        return True
    return any(rel_path.is_relative_to(Path(d)) for d in directories_to_link)


def dotted_destination(src: Path, source_root: Path, target_root: Path) -> Path:
    parts = src.relative_to(source_root).parts
    return target_root / Path("." + parts[0], *parts[1:])


def link_dotfiles(dotfiles_dir: Path, home_dir: Path, dirs_to_link):
    linked_count = skipped_count = 0
    for src in dotfiles_dir.rglob("*"):
        if not src.is_file() or should_skip(
            src.relative_to(dotfiles_dir), dirs_to_link
        ):
            skipped_count += 1
            continue
        if link_path(src, dotted_destination(src, dotfiles_dir, home_dir)):
            linked_count += 1
        else:
            skipped_count += 1
    return linked_count, skipped_count


def link_directories(dotfiles_dir: Path, home_dir: Path, dirs_to_link):
    linked_count = skipped_count = 0
    for dir_rel in dirs_to_link:
        src_dir = dotfiles_dir / dir_rel
        if src_dir.is_dir():
            if link_path(src_dir, dotted_destination(src_dir, dotfiles_dir, home_dir)):
                linked_count += 1
            else:
                skipped_count += 1
        else:
            skipped_count += 1
    return linked_count, skipped_count


def link_individual_dirs(individual_dirs):
    linked_count = skipped_count = 0
    for src_dir, dst_dir in individual_dirs:
        if not src_dir.is_dir():
            log.warning(f"Directory does not exist, skipping: {src_dir}")
            skipped_count += 1
            continue
        for src_file in src_dir.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(src_dir)
                dst_file = dst_dir / rel_path
                if link_path(src_file, dst_file):
                    linked_count += 1
                else:
                    skipped_count += 1
    return linked_count, skipped_count


def reload_hyprland():
    if shutil.which("hyprctl"):
        subprocess.run(["hyprctl", "reload"], check=False)
        log.info("Hyprland reloaded")


def deploy_dotfiles(dotfiles_dir: Path, home_dir: Path, dirs_to_link, individual_dirs):
    if not dotfiles_dir.is_dir():
        log.error(f"Error: {dotfiles_dir} does not exist!")
    else:
        linked_count = skipped_count = 0
        lc, sc = link_dotfiles(dotfiles_dir, home_dir, dirs_to_link)
        linked_count += lc
        skipped_count += sc
        lc, sc = link_directories(dotfiles_dir, home_dir, dirs_to_link)
        linked_count += lc
        skipped_count += sc
        lc, sc = link_individual_dirs(individual_dirs)
        linked_count += lc
        skipped_count += sc
        reload_hyprland()
        log.info(f"Linked: {linked_count} | Skipped: {skipped_count}")


if __name__ == "__main__":
    deploy_dotfiles(DOTFILES_DIR, HOME, DIRECTORIES_TO_LINK, INDIVIDUAL_DIRS)
