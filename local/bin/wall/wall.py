#!/usr/bin/env python3

import random
import shutil
import subprocess
from pathlib import Path
from wand.image import Image as WandImage
from wand.drawing import Drawing
from wand.color import Color

# ====================== Configuration ======================
HOME = Path.home()
WALLPAPER_DIR = HOME / ".local/bin/wall/wallpapers"
QUOTES_FILE = HOME / ".local/bin/wall/quotes.txt"
FONT_PATH = Path("/usr/share/fonts/OTF/FiraMonoNerdFont-Medium.otf")
CACHE_FILE = HOME / ".cache/wallpaper_with_quote.png"
LAST_WALLPAPER_FILE = CACHE_FILE.parent / ".last_wallpaper"
TEMP_RESIZED = HOME / ".cache/wallpaper_resized.png"
FONT_SIZE = 11
TEXT_COLOR = Color("rgba(229, 231, 235, 0.55)")
SHADOW_COLOR = Color("rgba(16, 16, 19, 1)")
SHADOW_OFFSET_X = 0
SHADOW_OFFSET_Y = 0
BOTTOM_PADDING = 1250
SIDE_PADDING = 200
TRANSITION_DURATION = 1.2


# ====================== Functions ======================
def get_screen_resolution() -> tuple[int, int]:
    output = subprocess.check_output(["hyprctl", "monitors"], text=True)
    for line in output.splitlines():
        if "x" in line and "@" in line:
            w, h = map(int, line.split("@")[0].strip().split("x"))
            return w, h
    return 1920, 1080


def random_wallpaper() -> Path | None:
    if not WALLPAPER_DIR.is_dir():
        return None
    images = [
        p
        for p in WALLPAPER_DIR.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ]
    if not images:
        return None
    last = (
        LAST_WALLPAPER_FILE.read_text().strip() if LAST_WALLPAPER_FILE.exists() else ""
    )
    candidates = [p for p in images if str(p) != last] or images
    selected = random.choice(candidates)
    LAST_WALLPAPER_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_WALLPAPER_FILE.write_text(str(selected))
    return selected


def random_quote() -> str:
    if not QUOTES_FILE.exists():
        return ""
    quotes = [
        line.strip() for line in QUOTES_FILE.read_text().splitlines() if line.strip()
    ]
    return random.choice(quotes) if quotes else ""


def resize_to_screen(image_path: Path) -> Path:
    screen_w, screen_h = get_screen_resolution()
    with WandImage(filename=str(image_path)) as img:
        img.transform(resize=f"{screen_w}x{screen_h}^")
        img.crop(
            left=max((img.width - screen_w) // 2, 0),
            top=max((img.height - screen_h) // 2, 0),
            width=screen_w,
            height=screen_h,
        )
        TEMP_RESIZED.parent.mkdir(parents=True, exist_ok=True)
        img.save(filename=str(TEMP_RESIZED))
    return TEMP_RESIZED


def add_quote_with_wand(image_path: Path, quote: str) -> Path:
    if not quote:
        return image_path
    with WandImage(filename=str(image_path)) as img:
        left, top = SIDE_PADDING, 200
        box_width, box_height = (
            img.width - 2 * SIDE_PADDING,
            img.height - BOTTOM_PADDING - 200,
        )
        text_x = int(left + box_width / 2)
        text_y = int(top + box_height / 2)
        # ---------------- Shadow layer ----------------
        with WandImage(
            width=img.width,
            height=img.height,
            background=Color("transparent"),
        ) as shadow_img:
            with Drawing() as shadow_draw:
                shadow_draw.font = str(FONT_PATH)
                shadow_draw.font_size = FONT_SIZE
                shadow_draw.fill_color = SHADOW_COLOR
                shadow_draw.text_alignment = "center"
                shadow_draw.gravity = "center"
                shadow_draw.text(
                    text_x + SHADOW_OFFSET_X,
                    text_y + SHADOW_OFFSET_Y,
                    quote,
                )
                shadow_draw(shadow_img)
            # Blur the shadow
            shadow_img.gaussian_blur(radius=0, sigma=1.5)
            # Composite shadow onto main image
            img.composite(shadow_img, 0, 0)
        # ---------------- Main text ----------------
        with Drawing() as draw:
            draw.font = str(FONT_PATH)
            draw.font_size = FONT_SIZE
            draw.fill_color = TEXT_COLOR
            draw.text_alignment = "center"
            draw.gravity = "center"
            draw.text(text_x, text_y, quote)
            draw(img)
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        img.save(filename=str(CACHE_FILE))
    return CACHE_FILE


def set_wallpaper(
    image_path: Path, transition_duration: float = TRANSITION_DURATION
) -> bool:
    if not shutil.which("swww") or not image_path.exists():
        return False
    try:
        subprocess.run(
            [
                "swww",
                "img",
                str(image_path),
                "--transition-type",
                "wipe",
                "--transition-duration",
                str(transition_duration),
                "--transition-fps",
                "144",
            ],
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


# ====================== Main ======================
def main():
    wallpaper = random_wallpaper()
    if not wallpaper:
        return
    quote = random_quote()
    final_image = add_quote_with_wand(resize_to_screen(wallpaper), quote)
    set_wallpaper(final_image)


if __name__ == "__main__":
    main()
