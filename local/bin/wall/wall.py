#!/usr/bin/env python3
import random
import textwrap
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional

# === Configuration ===
HOME = Path.home()
WALLPAPER_DIR = HOME / ".local/bin/wall/wallpapers"
QUOTES_FILE = HOME / ".local/bin/wall/quotes.txt"
FONT_PATH = Path("/usr/share/fonts/OTF/FiraMonoNerdFontMono-Medium.otf")
CACHE_FILE = HOME / ".cache/wallpaper_with_quote.png"
TEMP_RESIZED_FILE = (
    HOME / ".cache/wallpaper_resized.png"
)  # Temporary file for resized image

MAX_CHARS = 80  # Maximum characters per line for text wrapping
TEXT_COLOR = (229, 231, 235, 179)  # Text color with 60% opacity
SHADOW_COLOR = (16, 16, 19, 217)  # Shadow color with 80% opacity
SHADOW_BLUR_RADIUS = 1  # Blur radius for text shadow
VERT_MARGIN = 1057  # Vertical margin for text placement
X_OFFSET = -370


def get_screen_size() -> tuple[int, int]:
    """Detect screen size using hyprctl (Hyprland)."""
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
    """
    Select a random image file from the specified directory with given extensions.

    Args:
        directory (Path): Path to the directory to search.
        exts (tuple[str, ...]): Allowed file extensions (case-insensitive).

    Returns:
        Optional[Path]: Path to the randomly selected file, or None if not found or error occurs.
    """
    try:
        if not directory.is_dir():
            print(f"[ERROR] Not a directory: {directory}")
            return None

        files = [
            f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in exts
        ]
        if not files:
            print(f"[WARNING] No image files found in: {directory}")
            return None

        selected = random.choice(files)
        print(f"[INFO] Selected file: {selected.name}")
        return selected

    except Exception as e:
        print(f"[ERROR] Failed to select file from {directory}: {e}")
        return None


def get_random_quote(file_path: Path) -> str:
    """
    Select a random non-empty line (quote) from the given file.

    Args:
        file_path (Path): Path to the quotes text file.

    Returns:
        str: A randomly selected quote, or a message about where to place the file if missing.
    """
    try:
        if not file_path.exists():
            print(f"[ERROR] Quotes file not found at: {file_path}")

        with file_path.open("r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]

        if not quotes:
            print(f"[WARNING] Quote file at {file_path} is empty.")

        quote = random.choice(quotes)
        print(f"[INFO] Selected quote: {quote}")
        return quote

    except Exception as e:
        print(f"[ERROR] Failed to read quotes from file: {e}")


def resize_image_to_screen(image_path: Path) -> Path:
    """
    Resize the input image to fit the screen size while preserving aspect ratio.

    Args:
        image_path: Path to the input image

    Returns:
        Path to the resized image
    """
    try:
        # Load image
        image = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"[ERROR] Failed to open image for resizing: {e}")
        return image_path

    # Get screen size
    screen_width, screen_height = get_screen_size()

    # Calculate resize dimensions
    img_width, img_height = image.size
    aspect_ratio = img_width / img_height
    screen_aspect = screen_width / screen_height

    if aspect_ratio > screen_aspect:
        # Image is wider than screen, scale by height
        new_height = screen_height
        new_width = int(new_height * aspect_ratio)
    else:
        # Image is taller than screen, scale by width
        new_width = screen_width
        new_height = int(new_width / aspect_ratio)

    # Resize image
    try:
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"[INFO] Resized image to {new_width}x{new_height}")
    except Exception as e:
        print(f"[WARNING] Failed to resize image: {e}. Using original size.")
        return image_path

    # Center crop to exact screen size if needed
    if new_width != screen_width or new_height != screen_height:
        left = (new_width - screen_width) // 2
        top = (new_height - screen_height) // 2
        image = image.crop((left, top, left + screen_width, top + screen_height))

    # Save resized image
    TEMP_RESIZED_FILE.parent.mkdir(parents=True, exist_ok=True)
    image.save(TEMP_RESIZED_FILE, format="PNG")
    return TEMP_RESIZED_FILE


def draw_quote(image_path: Path, quote: str, x_offset: int) -> Path:
    """
    Overlay a quote onto an image with a shadow effect and save to cache.

    Args:
        image_path: Path to the input image
        quote: The text to overlay on the image

    Returns:
        Path to the output image with the quote
    """
    # Load and prepare the base image
    try:
        base = Image.open(image_path)
    except Exception as e:
        print(f"[ERROR] Failed to open image: {e}")
        return image_path

    width, height = base.size
    font_size = max(12, width // 155)

    # Load font or use default
    try:
        font = ImageFont.truetype(str(FONT_PATH), font_size)
    except Exception:
        print("[WARNING] Failed to load font, using default.")
        font = ImageFont.load_default()

    # Wrap quote into lines
    lines = textwrap.wrap(quote, width=MAX_CHARS)

    # Create layers for shadow and text
    txt_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_shadow = ImageDraw.Draw(shadow_layer)
    draw_text = ImageDraw.Draw(txt_layer)

    # Calculate starting y-position for text
    y = height - VERT_MARGIN - font_size * len(lines)

    # Draw shadow
    for line in lines:
        line_width = draw_text.textlength(line, font=font)
        x = (width - line_width) // 2 + x_offset
        draw_shadow.text((x, y), line, font=font, fill=SHADOW_COLOR)
        y += font_size

    # Apply blur to shadow
    blurred_shadow = shadow_layer.filter(
        ImageFilter.GaussianBlur(radius=SHADOW_BLUR_RADIUS)
    )
    combined = Image.alpha_composite(base, blurred_shadow)

    # Draw text
    y = height - VERT_MARGIN - font_size * len(lines)
    for line in lines:
        line_width = draw_text.textlength(line, font=font)
        x = (width - line_width) // 2 + x_offset
        draw_text.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += font_size

    # Save final image
    final = Image.alpha_composite(combined, txt_layer)
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    final.save(CACHE_FILE, format="PNG")

    return CACHE_FILE


def set_wallpaper(image_path: Path) -> bool:
    """
    Set the provided image as the desktop wallpaper using swww.

    Args:
        image_path: Path to the image to set as wallpaper

    Returns:
        True if wallpaper was set successfully, False otherwise
    """
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
    """
    Main function to select a random wallpaper, resize it, overlay a random quote, and set it as the desktop wallpaper.
    """
    # Select a random wallpaper
    wallpaper = choose_random_file(WALLPAPER_DIR)

    # Resize wallpaper to screen size
    resized_wallpaper = resize_image_to_screen(wallpaper)

    # Get a random quote
    quote = get_random_quote(QUOTES_FILE)

    # Overlay quote on the resized wallpaper
    final_img = draw_quote(resized_wallpaper, quote, X_OFFSET)

    # Set the final image as wallpaper
    if final_img.exists() and set_wallpaper(final_img):
        print("[INFO] Wallpaper updated successfully.")
    else:
        print("[ERROR] Failed to update wallpaper.")


if __name__ == "__main__":
    main()
