#!/usr/bin/env python3
"""
dotsync — Deploy dotfiles from Polka → ~/
All files/folders are always deployed to HOME with a leading dot.
Safely handles symlinks and real files, skips directories in SKIP.
"""

import os
import subprocess
from pathlib import Path
import fnmatch
from concurrent.futures import ThreadPoolExecutor

# === CONFIG ===
DOTDIRS = [
    Path.home() / "Polka",
    Path.home() / "Polka/secretdots",
]
DOTDIRS = [d for d in DOTDIRS if d.is_dir()]

# Names of directories/files to skip
SKIP = {".git", ".gitignore", "etc", "secretdots"}

print = lambda *a, **k: __builtins__.print("[Polka]", *a, **k)


# === CORE FUNCTIONS ===
def targets(src: Path) -> set[Path]:
    """Return relative paths of files to deploy, skipping SKIP."""
    res = set()
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        if any(fnmatch.fnmatch(p, pat) for p in rel.parts for pat in SKIP):
            continue
        # prepend dot to the first part
        rel = Path(f".{rel.parts[0]}", *rel.parts[1:])
        res.add(rel)
    return res


def check_overlap(sources):
    """Ensure multiple sources do not deploy to same destination."""
    cache = {}
    for src in sources:
        if not src.is_dir():
            continue
        cache[src] = {Path.home() / p for p in targets(src)}
    seen = list(cache.items())
    for i, (s1, t1) in enumerate(seen):
        for s2, t2 in seen[i + 1:]:
            overlap = t1 & t2
            if overlap:
                raise ValueError(f"Overlap: {s1} vs {s2}: {', '.join(map(str, overlap))}")
    return cache


def rm(p: Path):
    """Safely remove a path."""
    try:
        if p.is_symlink() or p.is_file():
            print(f"Remove: {p}")
            p.unlink(missing_ok=True)
        else:
            print(f"Skipping directory: {p}")
    except Exception as e:
        print(f"Failed to remove {p}: {e}")


def link(src: Path, dst: Path):
    """Create a relative symlink from src → dst."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    rel = os.path.relpath(src, dst.parent)
    print(f"Link: {dst} → {rel}")
    dst.symlink_to(rel)


def deploy_dir(src: Path):
    """Deploy all files from src → HOME with threads."""
    def job(f: Path):
        if not f.is_file():
            return
        rel = f.relative_to(src)
        if any(fnmatch.fnmatch(p, pat) for p in rel.parts for pat in SKIP):
            return
        dst = Path.home() / Path(f".{rel.parts[0]}", *rel.parts[1:])
        rm(dst)
        link(f, dst)

    with ThreadPoolExecutor() as pool:
        pool.map(job, src.rglob("*"))


def reload_hypr():
    """Reload Hyprland if available."""
    try:
        print("Reload Hyprland...")
        subprocess.run(["hyprctl", "reload"], check=True)
    except FileNotFoundError:
        print("hyprctl not found — skipping.")
    except Exception as e:
        print(f"Reload failed: {e}")


# === MAIN ===
def main():
    print("Starting Polka...")

    if not DOTDIRS:
        print("Nothing to deploy.")
        return

    try:
        check_overlap(DOTDIRS)
    except ValueError as e:
        print(f"Error: {e}")
        return

    for src_dir in DOTDIRS:
        print(f"Deploy dotfiles: {src_dir} → {Path.home()}")
        deploy_dir(src_dir)

    reload_hypr()
    print("Done!")


if __name__ == "__main__":
    main()
