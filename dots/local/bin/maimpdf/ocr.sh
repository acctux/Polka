#!/bin/bash

SRC="$(pwd)/screens"
DEST="$SRC/noalpha"

mkdir -p "$DEST"

# Remove alpha and save copies in DEST
mogrify -path "$DEST" -alpha remove -alpha off "$SRC"/*.png

# Create PDF from converted images
img2pdf $(ls -v "$DEST"/*.png) -o output.pdf

# OCR the PDF
ocrmypdf --language eng \
         --output-type pdf \
         --jpeg-quality 100 \
         output.pdf ocr_output.pdf

rm -rf "$DEST"
rm -f output.pdf
