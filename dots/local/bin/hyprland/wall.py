#!/usr/bin/env python3
import random
import textwrap
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# === Configuration ===
HOME = Path.home()
WALLPAPER_DIR = HOME / ".local/bin/hyprland/wallpapers"
QUOTES_FILE = HOME / ".local/bin/hyprland/quotes.txt"
FONT_PATH = Path("/usr/share/fonts/TTF/CaskaydiaMonoNerdFontMono-Regular.ttf")
CACHE_FILE = HOME / ".cache/wallpaper_with_quote.png"

MAX_CHARS = 300
TEXT_COLOR = (229, 231, 235, 128)   # 60% opacity
SHADOW_COLOR = (16, 16, 19, 230) # 80% opacity
SHADOW_BLUR_RADIUS = 1
VERT_MARGIN = 20


def choose_random_file(directory, exts=(".jpg", ".jpeg", ".png", ".webp")):
    try:
        files = [f for f in directory.iterdir() if f.suffix.lower() in exts and f.is_file()]
        print(f"[DEBUG] Files detected: {[f.name for f in files]}")
        if not files:
            return None
        choice = random.choice(files)
        print(f"[DEBUG] Chosen wallpaper: {choice.name}")
        return choice
    except Exception as e:
        print(f"[ERROR] Choosing wallpaper: {e}")
        return None

def get_random_quote(file_path):
    try:
        with file_path.open(encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        return random.choice(quotes) if quotes else "No quote today."
    except Exception as e:
        print(f"[ERROR] Reading quotes: {e}")
        return "No quote today."

def draw_quote(image_path, quote):
    try:
        base = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"[ERROR] Opening image: {e}")
        return image_path

    w, h = base.size
    font_size = max(12, w // 155)
    try:
        font = ImageFont.truetype(str(FONT_PATH), font_size)
    except:
        font = ImageFont.load_default()

    lines = textwrap.wrap(quote, width=MAX_CHARS)

    txt_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_shadow = ImageDraw.Draw(shadow_layer)
    draw_text = ImageDraw.Draw(txt_layer)

    y = h - VERT_MARGIN - font_size * len(lines)

    for line in lines:
        line_width = draw_text.textlength(line, font=font)
        x = (w - line_width) // 2  # center horizontally
        draw_shadow.text((x, y), line, font=font, fill=SHADOW_COLOR)
        y += font_size

    blurred_shadow = shadow_layer.filter(ImageFilter.GaussianBlur(radius=SHADOW_BLUR_RADIUS))
    combined = Image.alpha_composite(base, blurred_shadow)

    y = h - VERT_MARGIN - font_size * len(lines)
    for line in lines:
        line_width = draw_text.textlength(line, font=font)
        x = (w - line_width) // 2
        draw_text.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += font_size

    final = Image.alpha_composite(combined, txt_layer)

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    final.convert("RGB").save(CACHE_FILE)

    return CACHE_FILE

def set_wallpaper(image_path):
    if not shutil.which("swww"):
        print("[ERROR] 'swww' command not found.")
        return False
    try:
        subprocess.run(["swww", "img", str(image_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to set wallpaper: {e}")
        return False

def main():
    wallpaper = choose_random_file(WALLPAPER_DIR)
    if not wallpaper:
        print("[ERROR] No wallpaper found.")
        return

    quote = get_random_quote(QUOTES_FILE)
    final_img = draw_quote(wallpaper, quote)

    if final_img.exists() and set_wallpaper(final_img):
        print("[INFO] Wallpaper updated.")

if __name__ == "__main__":
    main()
