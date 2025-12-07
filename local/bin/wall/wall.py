#!/usr/bin/env python3
import random
import textwrap
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional

HOME = Path.home()
WALLPAPER_DIR = HOME / ".local/bin/wall/wallpapers"
QUOTES_FILE = HOME / ".local/bin/wall/quotes.txt"
FONT_PATH = Path("/usr/share/fonts/OTF/FiraMonoNerdFont-Medium.otf")
CACHE_FILE = HOME / ".cache/wallpaper_with_quote.png"
TEMP_RESIZED_FILE = HOME / ".cache/wallpaper_resized.png"
MAX_CHARS = 200
TEXT_COLOR = (229, 231, 235, 179)
SHADOW_COLOR = (16, 16, 19, 217)
SHADOW_BLUR_RADIUS = 2
VERT_MARGIN = 1066
X_OFFSET = 0
FONT_SIZE = 10


def get_screen_size() -> tuple[int, int]:
    try:
        output = subprocess.run(
            ["hyprctl", "monitors"], capture_output=True, text=True, check=True
        ).stdout
        for line in output.splitlines():
            if "@" in line and "x" in line:
                res_part = line.strip().split("@")[0].strip()
                width, height = map(int, res_part.split("x"))
                print(f"[INFO] Detected screen size via hyprctl: {width}x{height}")
                return width, height
    except Exception as e:
        print(f"[ERROR] Failed to detect screen size with hyprctl: {e}")
    print("[WARNING] Using default screen size: 1920x1080")
    return 1920, 1080


def choose_random_file(
    directory: Path, exts: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")
) -> Optional[Path]:
    if not directory.is_dir():
        print(f"[ERROR] Not a directory: {directory}")
        return None
    files = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in exts]
    if not files:
        print(f"[WARNING] No image files found in: {directory}")
        return None
    selected = random.choice(files)
    print(f"[INFO] Selected file: {selected.name}")
    return selected


def get_random_quote(file_path: Path) -> str:
    if not file_path.exists():
        print(f"[ERROR] Quotes file not found at: {file_path}")
    try:
        with file_path.open("r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        if not quotes:
            print(f"[WARNING] Quote file at {file_path} is empty.")
            return ""
        quote = random.choice(quotes)
        print(f"[INFO] Selected quote: {quote}")
        return quote
    except Exception as e:
        print(f"[ERROR] Failed to read quotes from file: {e}")
        return ""


def resize_image_to_screen(image_path: Path) -> Path:
    try:
        image = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"[ERROR] Failed to open image for resizing: {e}")
        return image_path
    screen_width, screen_height = get_screen_size()
    img_width, img_height = image.size
    aspect_ratio = img_width / img_height
    screen_aspect = screen_width / screen_height
    if aspect_ratio > screen_aspect:
        new_height = screen_height
        new_width = int(new_height * aspect_ratio)
    else:
        new_width = screen_width
        new_height = int(new_width / aspect_ratio)
    try:
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"[INFO] Resized image to {new_width}x{new_height}")
    except Exception as e:
        print(f"[WARNING] Failed to resize image: {e}. Using original size.")
        return image_path
    if new_width != screen_width or new_height != screen_height:
        left = (new_width - screen_width) // 2
        top = (new_height - screen_height) // 2
        image = image.crop((left, top, left + screen_width, top + screen_height))
    TEMP_RESIZED_FILE.parent.mkdir(parents=True, exist_ok=True)
    image.save(TEMP_RESIZED_FILE, format="PNG")
    return TEMP_RESIZED_FILE


def draw_quote(image_path: Path, quote: str, x_offset: int, font_size: int) -> Path:
    try:
        base = Image.open(image_path)
    except Exception as e:
        print(f"[ERROR] Failed to open image: {e}")
        return image_path
    width, height = base.size
    try:
        font = ImageFont.truetype(str(FONT_PATH), font_size)
    except Exception:
        print("[WARNING] Failed to load font, using default.")
        font = ImageFont.load_default()
    lines = textwrap.wrap(quote, width=MAX_CHARS)
    txt_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_shadow = ImageDraw.Draw(shadow_layer)
    draw_text = ImageDraw.Draw(txt_layer)
    y = height - VERT_MARGIN - font_size * len(lines)
    for line in lines:
        line_width = draw_text.textlength(line, font=font)
        x = (width - line_width) // 2 + x_offset
        draw_shadow.text((x, y), line, font=font, fill=SHADOW_COLOR)
        y += font_size
    blurred_shadow = shadow_layer.filter(
        ImageFilter.GaussianBlur(radius=SHADOW_BLUR_RADIUS)
    )
    combined = Image.alpha_composite(base, blurred_shadow)
    y = height - VERT_MARGIN - font_size * len(lines)
    for line in lines:
        line_width = draw_text.textlength(line, font=font)
        x = (width - line_width) // 2 + x_offset
        draw_text.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += font_size
    final = Image.alpha_composite(combined, txt_layer)
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    final.save(CACHE_FILE, format="PNG")
    return CACHE_FILE


def set_wallpaper(image_path: Path) -> bool:
    if not shutil.which("swww"):
        print("[ERROR] 'swww' command not found. Please ensure it is installed.")
        return False
    try:
        subprocess.run(["swww", "img", str(image_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to set wallpaper: {e}")
        return False


def main():
    wallpaper = choose_random_file(WALLPAPER_DIR)
    if wallpaper:
        resized_wallpaper = resize_image_to_screen(wallpaper)
        quote = get_random_quote(QUOTES_FILE)
        final_img = draw_quote(resized_wallpaper, quote, X_OFFSET, FONT_SIZE)
        if final_img.exists() and set_wallpaper(final_img):
            print("[INFO] Wallpaper updated successfully.")
        else:
            print("[ERROR] Failed to update wallpaper.")


if __name__ == "__main__":
    main()
