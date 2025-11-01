#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path
import os
import stat

# Define paths
HOME_BASE = Path("/home/nick").resolve()
DOTFILES_BASE = Path("/home/nick/Lit/dotfiles/Home").resolve()
STYLE_FILE = Path("~/.local/bin/wofi/fav_menu.css").expanduser()

def confirm_overwrite_graphical(target):
    """Prompt user to confirm overwrite using zenity."""
    try:
        result = subprocess.run(
            ["zenity", "--question", "--text", f"Overwrite existing file {target}?", "--width=300"],
            capture_output=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print(f"[WARNING] Zenity prompt failed, defaulting to no overwrite.")
        return False
    except FileNotFoundError:
        print(f"[ERROR] Zenity not installed, cannot prompt for overwrite.")
        return False

def check_permissions(path):
    """Check if the path is readable and writable."""
    try:
        return os.access(path, os.R_OK | os.W_OK)
    except Exception as e:
        print(f"[ERROR] Permission check failed for {path}: {e}")
        return False

def move_and_symlink(path):
    """Move a file or directory's contents to dotfiles and create symlinks."""
    original = Path(path).expanduser()
    try:
        original = original.resolve()  # Resolve symlinks
    except Exception as e:
        print(f"[ERROR] Failed to resolve path {path}: {e}")
        return

    if not original.exists():
        print(f"[ERROR] Path does not exist: {original}")
        return

    if not check_permissions(original):
        print(f"[ERROR] Insufficient permissions for {original}")
        return

    if original.is_dir():
        all_files = [p for p in original.rglob("*") if p.is_file() and not p.is_symlink()]
        if not all_files:
            print(f"[SKIPPED] No non-symlink files found in directory: {original}")
            return
        for file in all_files:
            process_single_file(file)
    elif original.is_file() and not original.is_symlink():
        process_single_file(original)
    else:
        print(f"[SKIPPED] Path is a symlink or not a regular file/directory: {original}")

def process_single_file(original):
    """Process a single file: move to dotfiles and create a symlink."""
    print(f"[DEBUG] Processing file: {original}")

    try:
        relative = original.relative_to(HOME_BASE)
        print(f"[DEBUG] Relative path: {relative}")
    except ValueError:
        print(f"[SKIPPED] Not under home directory: {original}")
        return

    target = DOTFILES_BASE / relative
    print(f"[DEBUG] Target path: {target}")

    if not check_permissions(target.parent):
        print(f"[ERROR] Insufficient permissions for target directory: {target.parent}")
        return

    # Check if target exists
    if target.exists() or target.is_symlink():
        print(f"[DEBUG] Target exists or is a symlink: {target}")
        if not confirm_overwrite_graphical(target):
            print(f"[SKIPPED] User chose not to overwrite {target}")
            return
        try:
            if target.is_file() or target.is_symlink():
                target.unlink()
            else:
                print(f"[ERROR] Cannot overwrite directory: {target}")
                return
        except Exception as e:
            print(f"[ERROR] Failed to remove existing target {target}: {e}")
            return

    try:
        # Create parent directories
        print(f"[DEBUG] Creating parent directories: {target.parent}")
        target.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        print(f"[DEBUG] Moving {original} to {target}")
        original.rename(target)
        print(f"[DEBUG] Move successful")

        # Create symlink
        print(f"[DEBUG] Creating symlink from {original} to {target}")
        os.symlink(target, original)
        print(f"[DEBUG] Symlink created")

        # Copy permissions
        original.chmod(target.stat().st_mode)
        print(f"[DEBUG] Permissions copied to symlink")

        notify_mako("Dotfiles Symlinked", f"{relative}")
        print(f"[OK] Moved {original} → {target} and created symlink.")

    except OSError as e:
        # Handle cross-device move
        if e.errno == 18:  # EXDEV: cross-device link
            print(f"[DEBUG] Cross-device move detected, copying instead")
            try:
                import shutil
                shutil.copy2(original, target)  # Copy with metadata
                original.unlink()  # Remove original
                os.symlink(target, original)  # Create symlink
                original.chmod(target.stat().st_mode)
                print(f"[OK] Copied {original} → {target} and created symlink.")
            except Exception as e:
                print(f"[ERROR] Failed to copy and symlink {original}: {e}")
        else:
            print(f"[ERROR] Failed to move and symlink {original}: {e}")

def refresh_nemo():
    """Force Nemo to refresh to ensure symlinks are displayed."""
    try:
        subprocess.run(["nemo", "-q"], capture_output=True)
        print("[DEBUG] Nemo refreshed")
    except subprocess.CalledProcessError:
        print("[WARNING] Failed to refresh Nemo")
    except FileNotFoundError:
        print("[WARNING] Nemo not installed, skipping refresh")

def main():
    """Main function to process command-line arguments."""
    if len(sys.argv) < 2:
        print("[ERROR] No files specified.")
        sys.exit(1)

    for path in sys.argv[1:]:
        move_and_symlink(path)

    # Refresh Nemo after all operations
    refresh_nemo()

if __name__ == "__main__":
    main()
