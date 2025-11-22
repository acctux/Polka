#!/usr/bin/env bash

waybar-module-music --marquee --format '%title%' -t 8 --effect-speed 1000 | awk '
{
    buf = buf $0

    while (match(buf, /\{[^}]*\}/)) {
        json = substr(buf, RSTART, RLENGTH)
        buf = substr(buf, RSTART + RLENGTH)

        # --- Capture the class (always preserved) ---
        class_val = ""
        if (match(json, /"class": "([^"]*)"/, c)) {
            class_val = c[1]
        }

        # --- Normalize text (remove No activity) ---
        gsub(/"text": "No activity"/, "\"text\": \"\"", json)

        # Extract text after normalization
        text_val = ""
        if (match(json, /"text": "([^"]*)"/, t)) {
            text_val = t[1]
        }

        # --- Add space before text if non-empty ---
        if (text_val != "") {
            text_val = " " text_val
        }

        # --- Reconstruct JSON with preserved class ---
        # Replace only the text field cleanly
        sub(/"text": "[^"]*"/, "\"text\": \"" text_val "\"", json)

        # Ensure class stays exactly what it was
        if (class_val != "") {
            sub(/"class": "[^"]*"/, "\"class\": \"" class_val "\"", json)
        }

        print json
        fflush()
    }
}
'
