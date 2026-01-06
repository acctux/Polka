#!/bin/bash

SRC="$HOME/Documents/Pictures/maimpdf/screens"
DEST="$SRC/noalpha"

mkdir -p "$DEST"
mogrify -path "$DEST" -alpha remove -alpha off "$SRC"/*.png
img2pdf $(ls -v "$DEST"/*.png) -o output.pdf
ocrmypdf --language eng \
  --output-type pdf \
  --jpeg-quality 100 \
  output.pdf ocr_output.pdf
rm -rf "$DEST"
rm -f output.pdf
