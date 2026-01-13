#!/bin/bash

SRC="$HOME/Documents/Pictures/maimpdf/screens"
DEST="$SRC/noalpha"
OUTPUT="$HOME/Documents/ocr_output.pdf"

mkdir -p "$DEST"
mogrify -path "$DEST" -alpha remove -alpha off "$SRC"/*.png
img2pdf $(ls -v "$DEST"/*.png) -o output.pdf
ocrmypdf --language eng --output-type pdf \
  --jpeg-quality 100 output.pdf $OUTPUT
rm -rf "$DEST"
rm -f output.pdf
