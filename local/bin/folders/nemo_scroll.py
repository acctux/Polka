#!/usr/bin/env python3
import json
import sys
import subprocess
from pathlib import Path


class NemoScroller:
    HOME = Path.home()
    CACHE_DIR = HOME / ".cache"
    INDEX_FILE = CACHE_DIR / "nemo_scroll_index"
    HIDE_FILE = CACHE_DIR / "nemo_scroll_hide"

    FOLDERS = [
        ("󱧶", f"xdg-open {HOME}/Documents"),
        ("󰉑", f"{HOME}/Polka/local/bin/folders/mountencrypted.sh"),
        ("󱂵", "xdg-open {HOME}/Polka"),
        ("󰉒", "xdg-open {HOME}/Lit/Noah"),
        ("󱂀", "xdg-open /etc"),
        ("󱁿", "xdg-open /usr/local/bin"),
    ]

    @classmethod
    def ensure_cache_dir(cls):
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def read_int_file(cls, path: Path, default: int = 0) -> int:
        try:
            return int(path.read_text().strip())
        except Exception:
            return default

    @classmethod
    def write_int_file(cls, path: Path, value: int) -> None:
        path.write_text(str(value))

    @classmethod
    def read_bool_file(cls, path: Path, default: bool = False) -> bool:
        try:
            return path.read_text().strip() == "1"
        except Exception:
            return default

    @classmethod
    def write_bool_file(cls, path: Path, value: bool) -> None:
        path.write_text("1" if value else "0")

    @classmethod
    def load_index(cls) -> int:
        cls.ensure_cache_dir()
        return cls.read_int_file(cls.INDEX_FILE, default=0)

    @classmethod
    def save_index(cls, index: int) -> None:
        cls.ensure_cache_dir()
        cls.write_int_file(cls.INDEX_FILE, index)

    @classmethod
    def load_hide(cls) -> bool:
        cls.ensure_cache_dir()
        return cls.read_bool_file(cls.HIDE_FILE, default=False)

    @classmethod
    def save_hide(cls, value: bool) -> None:
        cls.ensure_cache_dir()
        cls.write_bool_file(cls.HIDE_FILE, value)

    @classmethod
    def toggle_hide(cls) -> bool:
        new_hide = not cls.load_hide()
        cls.save_hide(new_hide)
        return new_hide

    @classmethod
    def scroll(cls, direction: str) -> None:
        index = cls.load_index()
        if direction == "up":
            index = (index + 1) % len(cls.FOLDERS)
        elif direction == "down":
            index = (index - 1) % len(cls.FOLDERS)
        cls.save_index(index)

    @classmethod
    def exec_current(cls) -> None:
        index = cls.load_index()
        _, cmd = cls.FOLDERS[index]
        subprocess.Popen([cmd])

    @classmethod
    def output_waybar(cls) -> None:
        index = cls.load_index()
        hide = cls.load_hide()
        icon, folder = cls.FOLDERS[index]
        folder_name = f" {Path(folder).name}" if not hide else ""
        waybar_class = "hidden" if hide else "visible"
        print(
            json.dumps(
                {
                    "text": f"{icon}<span size='8pt'>{folder_name}</span>",
                    "class": waybar_class,
                }
            )
        )

    @classmethod
    def run(cls, args) -> None:
        for arg in args:
            if arg in ("up", "down"):
                cls.scroll(arg)
                return
            elif arg == "exec":
                cls.exec_current()
                return
            elif arg == "toggle":
                cls.toggle_hide()
                return
        cls.output_waybar()


if __name__ == "__main__":
    NemoScroller.run(sys.argv[1:])
