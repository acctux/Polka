#!/usr/bin/env bash
set -euo pipefail  # Exit on error, undefined variable, or failed pipeline

# --- Configuration ---
# Directory containing wallpapers
WALLPAPER_DIR="$HOME/Lit/scripts/wall/wallpapers"
# File containing quotes (one per line)
QUOTES_FILE="${QUOTES_FILE:-$HOME/Lit/scripts/wall/quotes.txt}"
# Cache file to track the last used wallpaper
CURRENT_WALLPAPER_SOURCE_FILE="${XDG_CACHE_HOME:-$HOME/.cache}/wallpaper_quote_last_source.txt"
# Font to use for the quote
FONT="DejaVu-Sans"
# Font size (base pointsize; actual rendering size is scaled in ImageMagick)
POINTSIZE=4
# Vertical offset from the top for positioning the text/swatch (in pixels)
OFFSET_Y=1050
# Directory for storing generated final images
FINAL_IMG_DIR="${TMPDIR:-/tmp/wallpaperdaemon}"
# Text and swatch colors
TEXT_COLOR="white"
SWATCH_COLOR="rgba(16,16,19,0.5)"  # Semi-transparent dark background for quote
# Padding to add around the text (in pixels)
TEXT_PADDING_W=0
TEXT_PADDING_H=30
# Density for text rendering — higher = sharper text
MAGICK_DENSITY=220
# Toggle anti-aliasing for text rendering
#   1 = enable (smoother, better quality text)
#   0 = disable (pixelated or sharp edges; useful for debugging or terminal fonts)
MAGICK_ANTIALIAS=1
# Determines how much of the image width the quote should take up
QUOTE_WIDTH_RATIO=1
# Character wrap length for quotes (0 = no wrap)
QUOTE_CHAR_WRAP=0

log()   { echo "[INFO] $*" >&2; }
error() { echo "[ERROR] $*" >&2; }

start_swww_daemon() {
  [[ -z "$(pgrep -x swww-daemon)" ]] && swww-daemon & sleep 1
}

select_new_wallpaper() {
  local current="$1"
  local wallpapers new candidate

  mapfile -d '' wallpapers < <(find "$WALLPAPER_DIR" -type f \( -iname '*.jpg' -o -iname '*.png' -o -iname '*.webp' \) -print0)

  for try in {1..10}; do
    candidate=$(printf "%s\0" "${wallpapers[@]}" | shuf -z -n 1 | tr -d '\0')
    [[ "$candidate" != "$current" ]] && new="$candidate" && break
  done

  [[ -z "$new" ]] && new="$current"
  echo "$new"
}

select_random_quote() {
  [[ ! -r "$QUOTES_FILE" ]] && error "Quotes file missing." && exit 1

  local quote
  quote=$(shuf -n1 "$QUOTES_FILE" | sed 's/[“”]/"/g; s/[‘’]/'\''/g; s/[–—]/-/g')

  if [[ "$QUOTE_CHAR_WRAP" -gt 0 ]]; then
    quote=$(echo "$quote" | fold -s -w "$QUOTE_CHAR_WRAP")
  fi

  echo "$quote"
}

get_image_dimensions() {
  local image="$1"
  magick identify -format "%w %h" "$image"
}

calculate_caption_width() {
  local width="$1"
  awk -v width="$width" -v ratio="$QUOTE_WIDTH_RATIO" 'BEGIN { printf "%d", width * ratio }'
}

measure_quote_box() {
  local quote="$1"
  local caption_width="$2"
  magick -background none -fill white -font "$FONT" -pointsize "$POINTSIZE" -size "${caption_width}x" \
    caption:"$quote" -format "%w %h" info:
}

build_composited_image() {
  local wallpaper="$1"
  local quote="$2"
  local box_w="$3"
  local box_h="$4"
  local aa_flag="$5"
  local output_path="$6"

  #############################################################
  # 1. Start with the wallpaper as the base image.
  # 2. Draw a translucent rectangle ("swatch") to serve as the background for the text.
  # 3. Render the quote text as a transparent image.
  # 4. Composite the swatch and text over the wallpaper, aligned to top-center.
  #############################################################

  magick "$wallpaper" \
    \
    \( \
      -size "${box_w}x${box_h}" \
      xc:"$SWATCH_COLOR" \
    \) \
    -gravity north \
    -geometry +0+"$OFFSET_Y" \
    -compose over -composite \
    \
    \( \
      -background none \
      -density "$MAGICK_DENSITY" \
      $aa_flag \
      -pointsize $((POINTSIZE * 2)) \
      -font "$FONT" \
      -fill "$TEXT_COLOR" \
      -gravity center \
      label:"$quote" \
      -filter Lanczos \
      -resize 50% \
    \) \
    -gravity north \
    -geometry +0+"$OFFSET_Y" \
    -compose over -composite \
    \
    -quality 100 "$output_path"
}

compose_final_image() {
  local wallpaper="$1"
  local quote="$2"
  local box_w="$3"
  local box_h="$4"

  # Apply padding
  box_w=$((box_w + TEXT_PADDING_W))
  box_h=$((box_h + TEXT_PADDING_H))

  # Create output directory
  mkdir -p "$FINAL_IMG_DIR"

  # Determine antialias flag
  local aa_flag
  if [[ "$MAGICK_ANTIALIAS" -eq 1 ]]; then
    aa_flag="-antialias"
  else
    aa_flag="+antialias"
  fi

  # Create a temporary file for the final output
  local final_image
  final_image=$(mktemp "${FINAL_IMG_DIR}/wallpaper_quote_XXXXXX.jpg")

  # Delegate to ImageMagick command function
  build_composited_image "$wallpaper" "$quote" "$box_w" "$box_h" "$aa_flag" "$final_image"

  # Return the path to the generated image
  echo "$final_image"
}

main() {
  mkdir -p "$(dirname "$CURRENT_WALLPAPER_SOURCE_FILE")"
  mkdir -p "$FINAL_IMG_DIR"
  rm -f "${FINAL_IMG_DIR}"/wallpaper_quote_*.jpg

  start_swww_daemon

  local current new quote w h box_w box_h caption_width final_image

  current=$(< "$CURRENT_WALLPAPER_SOURCE_FILE" 2>/dev/null || echo "")
  new=$(select_new_wallpaper "$current")
  [[ -z "$new" ]] && error "No wallpapers found." && exit 1

  if [[ ! -f "$new" ]]; then
    error "Selected wallpaper does not exist: $new"
    exit 1
  fi

  quote=$(select_random_quote)
  [[ -z "$quote" ]] && error "Quote is empty." && exit 1

  read -r w h <<< "$(get_image_dimensions "$new")"
  caption_width=$(calculate_caption_width "$w")
  read -r box_w box_h <<< "$(measure_quote_box "$quote" "$caption_width")"

  final_image=$(compose_final_image "$new" "$quote" "$box_w" "$box_h")

  swww img "$final_image"
  echo "$new" > "$CURRENT_WALLPAPER_SOURCE_FILE"
  log "Wallpaper updated: $final_image"
}

main "$@"
